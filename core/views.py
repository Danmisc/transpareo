from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.conf import settings
from datetime import timedelta
from django.db.models import Q, Avg
import json

from .models import (
    Logement, Favori, LoginHistory, UserSession, 
    EmailVerificationToken, PasswordResetToken,
    ReclamationProprietaire, AvisLogement
)
from .forms import SignupForm, LoginForm, PasswordResetRequestForm, PasswordResetForm, ProfileUpdateForm
from .utils import (
    get_client_ip, 
    get_device_info, 
    send_verification_email, 
    send_password_reset_email,
    create_email_verification_token,
    create_password_reset_token,
    log_login_attempt,
    create_user_session,
    check_suspicious_login
)

User = get_user_model()


# ============================================
# VUE PRINCIPALE (LANDING PAGE)
# ============================================

def landing_page(request):
    """Page d'accueil avec pagination de 30 logements"""
    from django.core.paginator import Paginator
    
    # Paginer les logements (30 par page)
    all_logements = Logement.objects.all().order_by('-date_creation')
    paginator = Paginator(all_logements, 30)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Convertir UNIQUEMENT les 30 de cette page en JSON
    logements_json = json.dumps([
        {
            'id': l.id,
            'titre': l.titre,
            'adresse': l.adresse,
            'latitude': float(l.latitude),
            'longitude': float(l.longitude),
            'prix': float(l.prix),
            'surface': float(l.surface),
            'chambres': l.chambres,
            'type_logement': l.type_logement,
            'note': float(l.note_moyenne) if l.note_moyenne else 0,
            'description': l.description,
            'proprietaire_verifie': l.proprietaire is not None,
            'statut': l.statut,
        }
        for l in page_obj.object_list  # 👈 SEULEMENT les 30 de cette page
    ])
    
    # Compter les favoris
    favoris_count = 0
    if request.user.is_authenticated:
        favoris_count = Favori.objects.filter(utilisateur=request.user).count()
    
    context = {
        'page_obj': page_obj,
        'logements': page_obj.object_list,
        'logements_json': logements_json,
        'favoris_count': favoris_count,
        'total_logements': paginator.count,
    }
    
    return render(request, 'core/landing-page.html', context)




# ============================================
# DÉTAIL LOGEMENT
# ============================================

def logement_detail(request, id):
    """Page détail d'un logement avec tous les avis et infos"""
    logement = get_object_or_404(Logement, id=id)
    
    # Récupérer les avis vérifiés
    avis = logement.avis.filter(verifie=True).order_by('-date_avis')
    
    # Vérifier si l'utilisateur l'a en favori
    est_favori = False
    peut_laisser_avis = False
    peut_reclamer = False
    ma_reclamation = None
    
    if request.user.is_authenticated:
        est_favori = logement.favoris_utilisateurs.filter(utilisateur=request.user).exists()
        
        # Vérifier si l'utilisateur peut laisser un avis (pas déjà d'avis)
        peut_laisser_avis = not logement.avis.filter(locataire=request.user).exists()
        
        # Vérifier si l'utilisateur peut réclamer (et que ce n'est pas déjà réclamé)
        peut_reclamer = (
            logement.statut == 'disponible' and 
            not logement.reclamations.filter(utilisateur=request.user).exists()
        )
        
        # Récupérer sa reclamation si elle existe
        ma_reclamation = logement.reclamations.filter(utilisateur=request.user).first()
    
    context = {
        'logement': logement,
        'avis': avis,
        'est_favori': est_favori,
        'peut_laisser_avis': peut_laisser_avis,
        'peut_reclamer': peut_reclamer,
        'ma_reclamation': ma_reclamation,
        'avis_count': avis.count(),
        'note_moyenne': logement.note_moyenne,
    }
    
    return render(request, 'core/logement_detail.html', context)


# ============================================
# RÉCLAMATION PROPRIÉTAIRE
# ============================================

@login_required
def reclamer_bien(request, id):
    """Formulaire pour réclamer un bien (propriétaire)"""
    logement = get_object_or_404(Logement, id=id)
    
    # Vérifier que le bien n'est pas déjà réclamé
    if logement.statut != 'disponible':
        messages.error(request, "Ce bien a déjà été réclamé par un propriétaire.")
        return redirect('logement-detail', id=id)
    
    # Vérifier qu'il n'y a pas déjà une réclamation
    reclamation_existante = logement.reclamations.filter(utilisateur=request.user).first()
    if reclamation_existante:
        messages.info(request, f"Votre réclamation est en attente (statut: {reclamation_existante.get_statut_display()})")
        return redirect('logement-detail', id=id)
    
    if request.method == 'POST':
        message = request.POST.get('message', '')
        justificatif = request.FILES.get('justificatif')
        
        if not message:
            messages.error(request, "Veuillez expliquer pourquoi vous êtes le propriétaire.")
            return redirect('reclamer-bien', id=id)
        
        if not justificatif:
            messages.error(request, "Veuillez fournir un justificatif (taxe foncière, titre de propriété, etc.)")
            return redirect('reclamer-bien', id=id)
        
        # Créer la réclamation
        reclamation = ReclamationProprietaire.objects.create(
            logement=logement,
            utilisateur=request.user,
            message=message,
            justificatif=justificatif,
            statut='en_attente'
        )
        
        messages.success(request, "✅ Réclamation envoyée ! Un administrateur la vérifiera bientôt.")
        return redirect('logement-detail', id=id)
    
    return render(request, 'core/reclamer_bien.html', {'logement': logement})


# ============================================
# AVIS LOGEMENT
# ============================================

@login_required
def ajouter_avis(request, id):
    """Ajouter un avis sur un logement"""
    logement = get_object_or_404(Logement, id=id)
    
    # Vérifier que l'utilisateur n'a pas déjà d'avis
    avis_existant = logement.avis.filter(locataire=request.user).first()
    if avis_existant:
        messages.info(request, "Vous avez déjà laissé un avis sur ce logement.")
        return redirect('logement-detail', id=id)
    
    if request.method == 'POST':
        note = request.POST.get('note')
        titre = request.POST.get('titre')
        commentaire = request.POST.get('commentaire')
        note_proprete = request.POST.get('note_proprete')
        note_equipements = request.POST.get('note_equipements')
        note_localisation = request.POST.get('note_localisation')
        note_bailleur = request.POST.get('note_bailleur')
        justificatif = request.FILES.get('justificatif')
        
        # Validation
        if not all([note, titre, commentaire]):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return redirect('ajouter-avis', id=id)
        
        try:
            note = int(note)
            if not (1 <= note <= 5):
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "La note doit être entre 1 et 5.")
            return redirect('ajouter-avis', id=id)
        
        # Créer l'avis
        avis = AvisLogement.objects.create(
            logement=logement,
            locataire=request.user,
            note=note,
            titre=titre,
            commentaire=commentaire,
            note_proprete=int(note_proprete) if note_proprete else None,
            note_equipements=int(note_equipements) if note_equipements else None,
            note_localisation=int(note_localisation) if note_localisation else None,
            note_bailleur=int(note_bailleur) if note_bailleur else None,
            justificatif=justificatif,
            verifie=False
        )
        
        messages.success(request, "✅ Avis enregistré ! Un administrateur le vérifiera bientôt.")
        return redirect('logement-detail', id=id)
    
    return render(request, 'core/ajouter_avis.html', {'logement': logement})


@login_required
def mes_avis(request):
    """Liste des avis de l'utilisateur"""
    avis = AvisLogement.objects.filter(locataire=request.user).order_by('-date_avis')
    context = {'avis': avis}
    return render(request, 'core/mes_avis.html', context)


# ============================================
# BIENS DE L'UTILISATEUR (Propriétaire)
# ============================================

@login_required
def mes_biens(request):
    """Dashboard propriétaire - Ses biens"""
    biens = Logement.objects.filter(proprietaire=request.user)
    
    context = {
        'biens': biens,
        'total_biens': biens.count(),
        'biens_verifies': biens.filter(statut='verifie').count(),
    }
    
    return render(request, 'core/mes_biens.html', context)


# ============================================
# INSCRIPTION / CONNEXION / etc. (INCHANGÉ)
# ============================================

def signup_view(request):
    """Vue d'inscription avec validation avancée"""
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes déjà connecté.")
        return redirect('landing-page')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email_verified = False
            user.save()
            
            token = create_email_verification_token(user)
            
            try:
                send_verification_email(user, token.token)
                messages.success(request, f"✅ Compte créé ! Vérifiez votre email {user.email}")
            except Exception as e:
                messages.warning(request, f"⚠️ Compte créé mais erreur email: {str(e)}")
            
            login(request, user)
            log_login_attempt(user, request, success=True, reason="Inscription")
            create_user_session(user, request)
            
            return redirect('landing-page')
    else:
        form = SignupForm()
    
    return render(request, 'core/signup.html', {'form': form})


def login_view(request):
    """Vue de connexion"""
    if request.user.is_authenticated:
        messages.info(request, "Vous êtes déjà connecté.")
        return redirect('landing-page')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        email = request.POST.get('username')
        
        try:
            user = User.objects.get(email=email)
            
            if user.account_locked:
                if user.last_failed_login:
                    lockout_end = user.last_failed_login + timedelta(minutes=settings.LOCKOUT_DURATION)
                    if timezone.now() < lockout_end:
                        remaining = (lockout_end - timezone.now()).seconds // 60
                        messages.error(request, f"🔒 Compte verrouillé {remaining}min")
                        return render(request, 'core/login.html', {'form': form})
                    else:
                        user.account_locked = False
                        user.failed_login_attempts = 0
                        user.save()
            
            if form.is_valid():
                user = form.get_user()
                user.failed_login_attempts = 0
                user.last_ip = get_client_ip(request)
                user.save()
                
                login(request, user)
                log_login_attempt(user, request, success=True, reason="Connexion")
                create_user_session(user, request)
                messages.success(request, f"✅ Bienvenue {user.username}!")
                
                return redirect('landing-page')
            else:
                user.failed_login_attempts += 1
                user.last_failed_login = timezone.now()
                
                if user.failed_login_attempts >= settings.MAX_LOGIN_ATTEMPTS:
                    user.account_locked = True
                    messages.error(request, f"🔒 Compte verrouillé {settings.LOCKOUT_DURATION}min")
                else:
                    remaining = settings.MAX_LOGIN_ATTEMPTS - user.failed_login_attempts
                    messages.error(request, f"❌ Identifiants incorrects ({remaining} essais restants)")
                
                user.save()
                log_login_attempt(user, request, success=False, reason="Mot de passe incorrect")
        
        except User.DoesNotExist:
            messages.error(request, "❌ Email introuvable")
            form = LoginForm()
    
    else:
        form = LoginForm()
    
    return render(request, 'core/login.html', {'form': form})


@login_required
def logout_view(request):
    """Déconnexion"""
    try:
        session = UserSession.objects.get(
            user=request.user, 
            session_key=request.session.session_key
        )
        session.delete()
    except UserSession.DoesNotExist:
        pass
    
    logout(request)
    messages.success(request, "✅ Déconnecté")
    return redirect('landing-page')


def verify_email(request, token):
    """Vérification email"""
    try:
        verification = EmailVerificationToken.objects.get(token=token)
        if verification.is_valid():
            user = verification.user
            user.email_verified = True
            user.save()
            verification.used = True
            verification.save()
            messages.success(request, "✅ Email vérifié!")
            return redirect('profile')
        else:
            messages.error(request, "❌ Lien expiré")
            return redirect('landing-page')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, "❌ Lien invalide")
        return redirect('landing-page')


def password_reset_request(request):
    """Demande reset"""
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data['email'])
                token = create_password_reset_token(user, get_client_ip(request))
                try:
                    send_password_reset_email(user, token.token)
                    messages.success(request, "✅ Email de reset envoyé")
                except:
                    messages.error(request, "❌ Erreur envoi email")
            except User.DoesNotExist:
                messages.success(request, "✅ Si l'email existe, un lien a été envoyé")
            return redirect('login')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'core/password_reset_request.html', {'form': form})


def password_reset_confirm(request, token):
    """Confirmation reset"""
    try:
        reset_token = PasswordResetToken.objects.get(token=token)
        if not reset_token.is_valid():
            messages.error(request, "❌ Lien expiré")
            return redirect('password-reset-request')
        
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                user = reset_token.user
                user.set_password(form.cleaned_data['password1'])
                user.failed_login_attempts = 0
                user.account_locked = False
                user.save()
                reset_token.used = True
                reset_token.save()
                messages.success(request, "✅ Mot de passe changé!")
                return redirect('login')
        else:
            form = PasswordResetForm()
        
        return render(request, 'core/password_reset_confirm.html', {'form': form, 'token': token})
    
    except PasswordResetToken.DoesNotExist:
        messages.error(request, "❌ Lien invalide")
        return redirect('password-reset-request')


@login_required
def profile_view(request):
    """Profil utilisateur"""
    favoris_count = Favori.objects.filter(utilisateur=request.user).count()
    recent_logins = LoginHistory.objects.filter(user=request.user)[:10]
    active_sessions = UserSession.objects.filter(user=request.user)
    
    # Réclamations et avis de l'utilisateur
    mes_reclamations = ReclamationProprietaire.objects.filter(utilisateur=request.user)
    mes_avis = AvisLogement.objects.filter(locataire=request.user)
    
    context = {
        'favoris_count': favoris_count,
        'recent_logins': recent_logins,
        'active_sessions': active_sessions,
        'mes_reclamations': mes_reclamations,
        'mes_avis': mes_avis,
    }
    
    return render(request, 'core/profile.html', context)


@login_required
def profile_edit(request):
    """Édition profil"""
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Profil mis à jour!")
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'core/profile_edit.html', {'form': form})


@login_required
def security_settings(request):
    """Paramètres sécurité"""
    active_sessions = UserSession.objects.filter(user=request.user)
    login_history = LoginHistory.objects.filter(user=request.user)[:20]
    
    context = {
        'active_sessions': active_sessions,
        'login_history': login_history,
    }
    
    return render(request, 'core/security_settings.html', context)


@login_required
def revoke_session(request, session_id):
    """Révoquer session"""
    session = get_object_or_404(UserSession, id=session_id, user=request.user)
    session.delete()
    messages.success(request, "✅ Session révoquée")
    return redirect('security-settings')


# ============================================
# API FAVORIS
# ============================================

@require_http_methods(["GET"])
def api_get_user_favoris(request):
    """API favoris"""
    try:
        if request.user.is_authenticated:
            favoris = Favori.objects.filter(utilisateur=request.user).values_list('logement_id', flat=True)
            return JsonResponse({
                'authenticated': True,
                'favoris': list(favoris),
                'count': len(favoris),
            })
        else:
            return JsonResponse({
                'authenticated': False,
                'favoris': [],
                'count': 0,
            })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@require_http_methods(["POST"])
def api_toggle_favori(request):
    """Toggle favori"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        data = json.loads(request.body)
        logement_id = data.get('logement_id')
        
        logement = get_object_or_404(Logement, id=logement_id)
        favori, created = Favori.objects.get_or_create(
            utilisateur=request.user,
            logement=logement
        )
        
        if not created:
            favori.delete()
            return JsonResponse({'success': True, 'action': 'removed'})
        
        return JsonResponse({'success': True, 'action': 'added'})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ============================================
# CARTE ET FILTRES
# ============================================

def map_view(request):
    """Vue carte"""
    logements = Logement.objects.all()
    return render(request, 'core/map.html', {'logements': logements})


@require_http_methods(["GET"])
def api_filter_by_radius(request):
    """Filtre par rayon"""
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
        radius = float(request.GET.get('radius', 10))
        
        logements = Logement.objects.all()
        results = []
        
        for logement in logements:
            distance = ((logement.latitude - lat)**2 + (logement.longitude - lng)**2)**0.5
            if distance <= radius / 111:
                results.append({
                    'id': logement.id,
                    'titre': logement.titre,
                    'latitude': logement.latitude,
                    'longitude': logement.longitude,
                    'prix': float(logement.prix),
                })
        
        return JsonResponse({'logements': results})
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@require_http_methods(["GET"])
def api_get_logements(request):
    """API pour charger les logements paginés"""
    from django.core.paginator import Paginator
    
    try:
        page = int(request.GET.get('page', 1))
        
        all_logements = Logement.objects.all().order_by('-date_creation')
        paginator = Paginator(all_logements, 30)
        page_obj = paginator.get_page(page)
        
        data = {
            'logements': [
                {
                    'id': l.id,
                    'titre': l.titre,
                    'adresse': l.adresse,
                    'prix': float(l.prix),
                    'surface': float(l.surface),
                    'chambres': l.chambres,
                    'note': float(l.note_moyenne) if l.note_moyenne else 0,
                }
                for l in page_obj.object_list
            ],
            'page': page,
            'has_next': page_obj.has_next(),
            'total_pages': paginator.num_pages,
            'total_logements': paginator.count,
        }
        
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)



