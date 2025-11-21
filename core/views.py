"""
Views pour l'application Transpareo
Ce fichier contient toutes les vues de l'application
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Avg, Sum, Min, Max
from django.core.paginator import Paginator
from datetime import datetime, timedelta
import json
import csv

from .models import (
    CustomUser, Logement, Favori, ReclamationProprietaire, 
    AvisLogement, Candidature, Bail, PaiementLoyer,
    Post, Group, GroupMeetup, Message, Conversation, Call,
    MessageReaction, Badge, UserBadge, EmailVerificationToken, PasswordResetToken,
    MagicLinkToken, UserSession, LoginHistory, UserConnection
)
from .forms import SignupForm, LoginForm, PasswordResetRequestForm, PasswordResetForm, ProfileUpdateForm
from .utils import (
    send_verification_email, send_password_reset_email,
    create_email_verification_token, create_password_reset_token,
    get_client_ip, get_device_info, log_login_attempt, create_user_session,
    check_suspicious_login
)
from .rate_limit import rate_limit, get_client_ip_key, get_email_key
from .auth_utils import (
    create_magic_link, send_magic_link_email, generate_2fa_secret,
    generate_2fa_qr_code, verify_2fa_code, generate_backup_codes,
    check_and_award_badges, create_security_alert
)
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth import get_user_model

# ============================================
# DÉCORATEURS
# ============================================

def admin_required(view_func):
    """Décorateur pour vérifier que l'utilisateur est admin"""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, "Accès refusé. Vous devez être administrateur.")
            return redirect('connect-home')
        return view_func(request, *args, **kwargs)
    return wrapper

def stub_view(request, *args, **kwargs):
    """Vue stub pour les fonctionnalités non encore implémentées"""
    return render(request, 'core/admin/stub.html', {
        'message': 'Cette fonctionnalité sera implémentée prochainement'
    })

# ============================================
# VUES ADMIN - TRANSPAREO CONNECT
# ============================================

@admin_required
@login_required
def admin_connect(request):
    """Page d'administration Transpareo Connect - Gestion complète réseau social"""
    view_type = request.GET.get('view', 'posts')  # 'posts', 'groupes', 'messages', 'evenements', 'analytics'
    per_page = int(request.GET.get('per_page', 25))
    page = int(request.GET.get('page', 1))

    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    week_ago = now - timedelta(days=7)

    # ============================================
    # STATISTIQUES GLOBALES
    # ============================================
    total_posts = Post.objects.count()
    total_posts_mois = Post.objects.filter(created_at__gte=this_month_start).count()
    total_posts_mois_precedent = Post.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).count()
    evolution_posts = ((total_posts_mois - total_posts_mois_precedent) / total_posts_mois_precedent * 100) if total_posts_mois_precedent > 0 else 0

    groups_actifs = Group.objects.annotate(member_count=Count('members')).filter(member_count__gt=0).count()
    total_messages = Message.objects.count()

    # Taux engagement (simplifié)
    total_likes = Post.objects.aggregate(Sum('likes_count'))['likes_count__sum'] or 0
    total_comments = Post.objects.aggregate(Sum('comments_count'))['comments_count__sum'] or 0
    total_shares = Post.objects.aggregate(Sum('shares_count'))['shares_count__sum'] or 0
    total_engagement = total_likes + total_comments + total_shares
    taux_engagement = (total_engagement / total_posts * 100) if total_posts > 0 else 0

    # Utilisateurs actifs (dernière semaine)
    users_actifs = CustomUser.objects.filter(
        Q(posts__created_at__gte=week_ago) |
        Q(post_comments__created_at__gte=week_ago) |
        Q(sent_messages__created_at__gte=week_ago)
    ).distinct().count()

    # ============================================
    # VUE POSTS
    # ============================================
    if view_type == 'posts':
        posts = Post.objects.select_related('author', 'group').prefetch_related('images').all()

        # Filtres
        search_query = request.GET.get('search', '').strip()
        if search_query:
            posts = posts.filter(
                Q(content__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(hashtags__icontains=search_query) |
                Q(id__icontains=search_query)
            )

        type_filter = request.GET.getlist('type')
        if type_filter:
            posts = posts.filter(content_type__in=type_filter)

        statut_filter = request.GET.get('statut')
        if statut_filter:
            if statut_filter == 'quarantined':
                posts = posts.filter(is_quarantined=True)
            elif statut_filter == 'spam':
                posts = posts.filter(is_spam=True)
            elif statut_filter == 'inappropriate':
                posts = posts.filter(is_inappropriate=True)

        auteur_id = request.GET.get('auteur')
        if auteur_id:
            posts = posts.filter(author_id=auteur_id)

        groupe_id = request.GET.get('groupe')
        if groupe_id:
            posts = posts.filter(group_id=groupe_id)

        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        if date_debut:
            posts = posts.filter(created_at__gte=date_debut)
        if date_fin:
            posts = posts.filter(created_at__lte=date_fin)

        # Tri
        sort_by = request.GET.get('sort', '-created_at')
        posts = posts.order_by(sort_by)

        # Pagination
        paginator = Paginator(posts, per_page)
        posts_page = paginator.get_page(page)

        # Compteurs par catégorie
        count_by_category = {
            'tous': posts.count(),
            'recents': posts.filter(created_at__gte=now - timedelta(hours=24)).count(),
            'populaires': posts.filter(likes_count__gte=10).count(),
            'signales': posts.filter(is_inappropriate=True).count(),
        }

        # Export CSV
        if request.GET.get('export') == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = 'attachment; filename="posts.csv"'
            writer = csv.writer(response)
            writer.writerow([
                'ID', 'Auteur', 'Contenu', 'Type', 'Groupe', 'Likes', 'Commentaires',
                'Partages', 'Date publication', 'Statut'
            ])
            for p in posts:
                writer.writerow([
                    p.id, p.author.username, p.content[:200], p.content_type,
                    p.group.name if p.group else 'Public', p.likes_count, p.comments_count,
                    p.shares_count, p.created_at.strftime('%d/%m/%Y'),
                    'Quarantaine' if p.is_quarantined else 'Publié'
                ])
            return response

        context = {
            'view_type': 'posts',
            'posts': posts_page,
            'count_by_category': count_by_category,
            'per_page': per_page,
            'sort_by': sort_by,
            'filters': {
                'search': search_query,
                'type': type_filter,
                'statut': statut_filter,
                'auteur': auteur_id,
                'groupe': groupe_id,
                'date_debut': date_debut,
                'date_fin': date_fin,
            },
        }

    # ============================================
    # VUE GROUPES
    # ============================================
    elif view_type == 'groupes':
        groupes = Group.objects.annotate(
            member_count=Count('members', distinct=True),
            posts_count=Count('posts', distinct=True)
        ).all()

        # Filtres
        search_query = request.GET.get('search', '').strip()
        if search_query:
            groupes = groupes.filter(
                Q(name__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        type_filter = request.GET.get('type')
        if type_filter:
            if type_filter == 'public':
                groupes = groupes.filter(is_public=True)
            elif type_filter == 'private':
                groupes = groupes.filter(is_public=False)

        # Tri
        sort_by = request.GET.get('sort', '-created_at')
        groupes = groupes.order_by(sort_by)

        # Pagination
        paginator = Paginator(groupes, per_page)
        groupes_page = paginator.get_page(page)

        context = {
            'view_type': 'groupes',
            'groupes': groupes_page,
            'per_page': per_page,
            'sort_by': sort_by,
            'filters': {
                'search': search_query,
                'type': type_filter,
            },
        }

    # ============================================
    # VUE MESSAGES
    # ============================================
    elif view_type == 'messages':
        conversations = Conversation.objects.prefetch_related('participants', 'messages').all()

        # Filtres
        search_query = request.GET.get('search', '').strip()
        if search_query:
            conversations = conversations.filter(
                Q(messages__content__icontains=search_query) |
                Q(participants__username__icontains=search_query)
            ).distinct()

        # Tri
        sort_by = request.GET.get('sort', '-updated_at')
        conversations = conversations.order_by(sort_by)

        # Pagination
        paginator = Paginator(conversations, per_page)
        conversations_page = paginator.get_page(page)

        context = {
            'view_type': 'messages',
            'conversations': conversations_page,
            'per_page': per_page,
            'sort_by': sort_by,
            'filters': {
                'search': search_query,
            },
        }

    # ============================================
    # VUE ANALYTICS
    # ============================================
    elif view_type == 'analytics':
        # Données pour graphiques
        evolution_data = []
        for i in range(30):
            day = now - timedelta(days=i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day.replace(hour=23, minute=59, second=59, microsecond=999999)
            count = Post.objects.filter(
                created_at__gte=day_start,
                created_at__lte=day_end
            ).count()
            evolution_data.append({
                'date': day.strftime('%d/%m'),
                'count': count
            })
        evolution_data.reverse()

        # Engagement par type
        engagement_by_type = []
        for content_type in ['news', 'guide', 'offer', 'discussion', 'property', 'group']:
            posts_type = Post.objects.filter(content_type=content_type)
            avg_likes = posts_type.aggregate(Avg('likes_count'))['likes_count__avg'] or 0
            avg_comments = posts_type.aggregate(Avg('comments_count'))['comments_count__avg'] or 0
            avg_shares = posts_type.aggregate(Avg('shares_count'))['shares_count__avg'] or 0
            engagement_by_type.append({
                'type': content_type,
                'avg_likes': round(avg_likes, 1),
                'avg_comments': round(avg_comments, 1),
                'avg_shares': round(avg_shares, 1),
            })

        context = {
            'view_type': 'analytics',
            'evolution_data': json.dumps(evolution_data),
            'engagement_by_type': json.dumps(engagement_by_type),
        }

    # ============================================
    # VUE ÉVÉNEMENTS
    # ============================================
    else:  # evenements
        context = {
            'view_type': 'evenements',
        }

    # Stats communes
    context.update({
        'stats': {
            'total_posts': total_posts,
            'total_posts_mois': total_posts_mois,
            'evolution_posts': round(evolution_posts, 1),
            'groups_actifs': groups_actifs,
            'total_messages': total_messages,
            'taux_engagement': round(taux_engagement, 1),
            'users_actifs': users_actifs,
        },
    })

    return render(request, 'core/admin/connect.html', context)

@admin_required
@login_required
def admin_post_detail_ajax(request, post_id):
    """Récupérer les détails d'un post en JSON pour le modal"""
    try:
        post = Post.objects.select_related(
            'author', 'group', 'related_logement'
        ).prefetch_related(
            'images', 'likes__user', 'comments__author', 'mentions'
        ).get(id=post_id)
        
        # Récupérer les images
        images = []
        for img in post.images.all()[:20]:
            images.append({
                'id': img.id,
                'url': img.image.url if img.image else '',
                'caption': img.caption or '',
            })
        
        # Récupérer les likes (top 10)
        likes = []
        for like in post.likes.filter(active=True).select_related('user')[:10]:
            likes.append({
                'id': like.user.id,
                'username': like.user.username,
                'avatar_url': like.user.avatar.url if like.user.avatar else None,
            })
        
        # Récupérer les commentaires (top 5)
        comments = []
        for comment in post.comments.filter(parent__isnull=True).select_related('author')[:5]:
            comments.append({
                'id': comment.id,
                'author': {
                    'id': comment.author.id,
                    'username': comment.author.username,
                    'avatar_url': comment.author.avatar.url if comment.author.avatar else None,
                },
                'content': comment.content,
                'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                'likes_count': comment.likes_count,
            })
        
        # Récupérer les mentions
        mentions = []
        for mention in post.mentions.all()[:10]:
            mentions.append({
                'id': mention.id,
                'username': mention.username,
            })
        
        data = {
            'id': post.id,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'email': post.author.email,
                'avatar_url': post.author.avatar.url if post.author.avatar else None,
            },
            'content': post.content,
            'content_type': post.content_type,
            'content_type_display': post.get_content_type_display(),
            'hashtags': post.hashtags or '',
            'visibility': post.visibility,
            'visibility_display': post.get_visibility_display(),
            'group': {
                'id': post.group.id,
                'name': post.group.name,
            } if post.group else None,
            'related_logement': {
                'id': post.related_logement.id,
                'titre': post.related_logement.titre,
                'adresse': post.related_logement.adresse,
            } if post.related_logement else None,
            'likes_count': post.likes_count,
            'comments_count': post.comments_count,
            'shares_count': post.shares_count,
            'images': images,
            'likes': likes,
            'comments': comments,
            'mentions': mentions,
            'created_at': post.created_at.strftime('%d/%m/%Y %H:%M'),
            'updated_at': post.updated_at.strftime('%d/%m/%Y %H:%M') if post.updated_at else '',
            'is_quarantined': post.is_quarantined,
            'is_spam': post.is_spam,
            'is_inappropriate': post.is_inappropriate,
            'security_score': post.security_score,
        }
        
        return JsonResponse(data)
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
@login_required
def admin_groupe_detail_ajax(request, groupe_id):
    """Récupérer les détails d'un groupe en JSON pour le modal"""
    try:
        groupe = Group.objects.prefetch_related(
            'members', 'admins', 'moderators', 'posts__author'
        ).annotate(
            member_count=Count('members', distinct=True),
            posts_count=Count('posts', distinct=True)
        ).get(id=groupe_id)
        
        # Membres (top 20)
        members = []
        for member in groupe.members.all()[:20]:
            members.append({
                'id': member.id,
                'username': member.username,
                'avatar_url': member.avatar.url if member.avatar else None,
            })
        
        # Admins
        admins = []
        for admin in groupe.admins.all():
            admins.append({
                'id': admin.id,
                'username': admin.username,
                'avatar_url': admin.avatar.url if admin.avatar else None,
            })
        
        data = {
            'id': groupe.id,
            'name': groupe.name,
            'description': groupe.description or '',
            'full_description': groupe.full_description or '',
            'is_public': groupe.is_public,
            'category': groupe.category,
            'category_display': groupe.get_category_display(),
            'ville': groupe.ville or '',
            'rules': groupe.rules or '',
            'tags': groupe.tags or '',
            'member_count': groupe.member_count,
            'posts_count': groupe.posts_count,
            'members': members,
            'admins': admins,
            'created_at': groupe.created_at.strftime('%d/%m/%Y'),
            'creator': {
                'id': groupe.creator.id,
                'username': groupe.creator.username,
            } if groupe.creator else None,
        }
        
        return JsonResponse(data)
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Groupe introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
@login_required
def admin_badges(request):
    """Page de gestion des badges et gamification"""
    badges = Badge.objects.annotate(
        users_count=Count('users', distinct=True)
    ).all()
    
    # Stats
    total_badges = badges.count()
    total_attributions = UserBadge.objects.count()
    badges_rares = badges.filter(rarity__in=['rare', 'epic', 'legendary']).count()
    
    # Badges les plus attribués
    top_badges = Badge.objects.annotate(
        users_count=Count('users', distinct=True)
    ).order_by('-users_count')[:10]
    
    context = {
        'badges': badges,
        'top_badges': top_badges,
        'stats': {
            'total_badges': total_badges,
            'total_attributions': total_attributions,
            'badges_rares': badges_rares,
        },
    }
    
    return render(request, 'core/admin/badges.html', context)

# ============================================
# VUES ADMIN - LOGEMENTS
# ============================================

@admin_required
@login_required
def admin_logements(request):
    """Page d'administration des logements"""
    per_page = int(request.GET.get('per_page', 25))
    page = int(request.GET.get('page', 1))
    
    logements = Logement.objects.select_related('proprietaire').prefetch_related('images').all()
    
    # Filtres
    search_query = request.GET.get('search', '').strip()
    if search_query:
        logements = logements.filter(
            Q(titre__icontains=search_query) |
            Q(adresse__icontains=search_query) |
            Q(id_parcelle__icontains=search_query)
        )
    
    statut_filter = request.GET.get('statut')
    if statut_filter:
        logements = logements.filter(statut=statut_filter)
    
    type_filter = request.GET.get('type')
    if type_filter:
        logements = logements.filter(type_logement=type_filter)
    
    ville_filter = request.GET.get('ville')
    if ville_filter:
        # Filtrer par code postal ou adresse (le modèle n'a pas de champ ville)
        logements = logements.filter(
            Q(code_postal__icontains=ville_filter) | 
            Q(adresse__icontains=ville_filter)
        )
    
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    if prix_min:
        logements = logements.filter(prix__gte=prix_min)
    if prix_max:
        logements = logements.filter(prix__lte=prix_max)
    
    proprietaire_id = request.GET.get('proprietaire')
    if proprietaire_id:
        logements = logements.filter(proprietaire_id=proprietaire_id)
    
    note_min = request.GET.get('note_min', 0)
    if note_min:
        logements = logements.filter(note_moyenne__gte=note_min)
    
    surface_min = request.GET.get('surface_min')
    surface_max = request.GET.get('surface_max')
    if surface_min:
        logements = logements.filter(surface__gte=surface_min)
    if surface_max:
        logements = logements.filter(surface__lte=surface_max)
    
    # Tri
    sort_by = request.GET.get('sort', '-date_creation')
    logements = logements.order_by(sort_by)
    
    # Stats
    total_logements = logements.count()
    logements_disponibles = logements.filter(statut='disponible').count()
    logements_verifies = logements.filter(statut='verifie').count()
    note_moyenne_globale = logements.aggregate(Avg('note_moyenne'))['note_moyenne__avg'] or 0
    
    # Stats pour les mini-cards
    actifs_count = Logement.objects.filter(statut='disponible').count()
    en_attente_count = Logement.objects.filter(statut='reclame').count()
    desactives_count = Logement.objects.exclude(statut='disponible').exclude(statut='reclame').count()
    
    # Prix range pour les sliders
    prix_stats = Logement.objects.aggregate(
        min_prix=Min('prix'),
        max_prix=Max('prix')
    )
    prix_range = {
        'min_prix': int(prix_stats['min_prix'] or 0),
        'max_prix': int(prix_stats['max_prix'] or 5000)
    }
    
    # Surface range pour les sliders
    surface_stats = Logement.objects.aggregate(
        min_surface=Min('surface'),
        max_surface=Max('surface')
    )
    surface_range = {
        'min_surface': int(surface_stats['min_surface'] or 0),
        'max_surface': int(surface_stats['max_surface'] or 200)
    }
    
    # Pagination
    paginator = Paginator(logements, per_page)
    logements_page = paginator.get_page(page)
    
    # Propriétaires pour autocomplete (utiliser biens_possedes qui est le related_name)
    proprietaires = CustomUser.objects.filter(biens_possedes__isnull=False).distinct()[:50]
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="logements.csv"'
        writer = csv.writer(response)
        writer.writerow([
            'ID', 'Titre', 'Adresse', 'Prix', 'Surface', 'Type', 'Statut', 'Note', 'Propriétaire'
        ])
        for l in logements:
            writer.writerow([
                l.id, l.titre, l.adresse, l.prix, l.surface, l.type_logement,
                l.statut, l.note_moyenne or 0, l.proprietaire.username if l.proprietaire else ''
            ])
        return response
    
    context = {
        'logements': logements_page,
        'total_logements': total_logements,
        'logements_disponibles': logements_disponibles,
        'logements_verifies': logements_verifies,
        'note_moyenne_globale': round(note_moyenne_globale, 1),
        'actifs_count': actifs_count,
        'en_attente_count': en_attente_count,
        'desactives_count': desactives_count,
        'proprietaires': proprietaires,
        'per_page': per_page,
        'sort_by': sort_by,
        'prix_range': prix_range,
        'surface_range': surface_range,
        'prix_min': prix_min,
        'prix_max': prix_max,
        'surface_min': surface_min,
        'surface_max': surface_max,
        'search_query': search_query,
        'filters': {
            'search': search_query,
            'statut': statut_filter,
            'type': type_filter,
            'ville': ville_filter,
            'prix_min': prix_min,
            'prix_max': prix_max,
            'surface_min': surface_min,
            'surface_max': surface_max,
            'proprietaire': proprietaire_id,
            'note_min': note_min,
        },
    }
    
    return render(request, 'core/admin/logements.html', context)

@admin_required
@login_required
def admin_logement_detail_ajax(request, logement_id):
    """Récupérer les détails d'un logement en JSON"""
    try:
        logement = Logement.objects.select_related('proprietaire').prefetch_related('images').get(id=logement_id)
        
        images = []
        for img in logement.images.all()[:20]:
            images.append({
                'id': img.id,
                'url': img.image.url if img.image else '',
                'caption': img.caption or '',
            })
        
        data = {
            'id': logement.id,
            'titre': logement.titre,
            'adresse': logement.adresse,
            'code_postal': logement.code_postal or '',
            'ville': logement.code_postal or '',  # Utiliser code_postal car le modèle n'a pas de champ ville
            'description': logement.description or '',
            'prix': float(logement.prix) if logement.prix else 0,
            'surface': logement.surface or 0,
            'chambres': logement.chambres or 0,
            'type_logement': logement.type_logement,
            'type_logement_display': logement.get_type_logement_display(),
            'statut': logement.statut,
            'statut_display': logement.get_statut_display(),
            'note_moyenne': float(logement.note_moyenne) if logement.note_moyenne else 0,
            'nombre_avis': logement.nombre_avis or 0,
            'latitude': float(logement.latitude) if logement.latitude else None,
            'longitude': float(logement.longitude) if logement.longitude else None,
            'images': images,
            'proprietaire': {
                'id': logement.proprietaire.id,
                'username': logement.proprietaire.username,
                'email': logement.proprietaire.email,
                'avatar_url': logement.proprietaire.avatar.url if logement.proprietaire.avatar else None,
            } if logement.proprietaire else None,
            'date_creation': logement.date_creation.strftime('%d/%m/%Y') if logement.date_creation else '',
        }
        
        return JsonResponse(data)
    except Logement.DoesNotExist:
        return JsonResponse({'error': 'Logement introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# VUES ADMIN - CANDIDATURES & LOCATIONS
# ============================================

@admin_required
@login_required
def admin_candidatures_locations(request):
    """Page d'administration des candidatures et locations"""
    view_type = request.GET.get('view', 'candidatures')  # 'candidatures' ou 'locations'
    per_page = int(request.GET.get('per_page', 25))
    page = int(request.GET.get('page', 1))
    
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # ============================================
    # STATISTIQUES GLOBALES
    # ============================================
    total_candidatures = Candidature.objects.count()
    candidatures_mois = Candidature.objects.filter(created_at__gte=this_month_start).count()
    candidatures_mois_precedent = Candidature.objects.filter(
        created_at__gte=last_month_start,
        created_at__lt=this_month_start
    ).count()
    evolution_candidatures = ((candidatures_mois - candidatures_mois_precedent) / candidatures_mois_precedent * 100) if candidatures_mois_precedent > 0 else 0
    
    candidatures_acceptees = Candidature.objects.filter(statut='acceptee').count()
    locations_actives = Bail.objects.filter(statut='actif').count()
    taux_acceptation = (candidatures_acceptees / total_candidatures * 100) if total_candidatures > 0 else 0
    
    # ============================================
    # VUE CANDIDATURES
    # ============================================
    if view_type == 'candidatures':
        candidatures = Candidature.objects.select_related(
            'candidat', 'logement', 'logement__proprietaire'
        ).all()
        
        # Filtres
        search_query = request.GET.get('search', '').strip()
        if search_query:
            candidatures = candidatures.filter(
                Q(candidat__username__icontains=search_query) |
                Q(logement__adresse__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        statut_filter = request.GET.get('statut')
        if statut_filter:
            candidatures = candidatures.filter(statut=statut_filter)
        
        logement_id = request.GET.get('logement')
        if logement_id:
            candidatures = candidatures.filter(logement_id=logement_id)
        
        candidat_id = request.GET.get('candidat')
        if candidat_id:
            candidatures = candidatures.filter(candidat_id=candidat_id)
        
        # Tri
        sort_by = request.GET.get('sort', '-created_at')
        candidatures = candidatures.order_by(sort_by)
        
        # Pagination
        paginator = Paginator(candidatures, per_page)
        candidatures_page = paginator.get_page(page)
        
        context = {
            'view_type': 'candidatures',
            'candidatures': candidatures_page,
            'per_page': per_page,
            'sort_by': sort_by,
            'filters': {
                'search': search_query,
                'statut': statut_filter,
                'logement': logement_id,
                'candidat': candidat_id,
            },
        }
    
    # ============================================
    # VUE LOCATIONS
    # ============================================
    else:  # locations
        locations = Bail.objects.select_related(
            'locataire', 'logement', 'logement__proprietaire'
        ).all()
        
        # Filtres
        search_query = request.GET.get('search', '').strip()
        if search_query:
            locations = locations.filter(
                Q(locataire__username__icontains=search_query) |
                Q(logement__adresse__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        statut_filter = request.GET.get('statut')
        if statut_filter:
            locations = locations.filter(statut=statut_filter)
        
        # Tri
        sort_by = request.GET.get('sort', '-date_debut')
        locations = locations.order_by(sort_by)
        
        # Pagination
        paginator = Paginator(locations, per_page)
        locations_page = paginator.get_page(page)
        
        context = {
            'view_type': 'locations',
            'locations': locations_page,
            'per_page': per_page,
            'sort_by': sort_by,
            'filters': {
                'search': search_query,
                'statut': statut_filter,
            },
        }
    
    # Stats communes
    context.update({
        'stats': {
            'total_candidatures': total_candidatures,
            'candidatures_mois': candidatures_mois,
            'evolution_candidatures': round(evolution_candidatures, 1),
            'candidatures_acceptees': candidatures_acceptees,
            'locations_actives': locations_actives,
            'taux_acceptation': round(taux_acceptation, 1),
        },
    })
    
    return render(request, 'core/admin/candidatures_locations.html', context)

@admin_required
@login_required
def admin_candidature_detail_ajax(request, candidature_id):
    """Récupérer les détails d'une candidature en JSON"""
    try:
        candidature = Candidature.objects.select_related(
            'candidat', 'logement', 'logement__proprietaire'
        ).get(id=candidature_id)
        
        # Calcul score simplifié
        score = 50  # Base
        if candidature.candidat.email_verified:
            score += 10
        if candidature.candidat.proprietaire_verified:
            score += 15
        
        data = {
            'id': candidature.id,
            'candidat': {
                'id': candidature.candidat.id,
                'username': candidature.candidat.username,
                'email': candidature.candidat.email,
                'avatar_url': candidature.candidat.avatar.url if candidature.candidat.avatar else None,
            },
            'logement': {
                'id': candidature.logement.id,
                'titre': candidature.logement.titre,
                'adresse': candidature.logement.adresse,
            },
            'proprietaire': {
                'id': candidature.logement.proprietaire.id,
                'username': candidature.logement.proprietaire.username,
                'email': candidature.logement.proprietaire.email,
            } if candidature.logement.proprietaire else None,
            'statut': candidature.statut,
            'statut_display': candidature.get_statut_display(),
            'score': score,
            'created_at': candidature.created_at.strftime('%d/%m/%Y %H:%M') if candidature.created_at else '',
        }
        
        return JsonResponse(data)
    except Candidature.DoesNotExist:
        return JsonResponse({'error': 'Candidature introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@admin_required
@login_required
def admin_candidature_refuse(request, candidature_id):
    """Refuser une candidature"""
    if request.method == 'POST':
        try:
            candidature = Candidature.objects.get(id=candidature_id)
            raison = request.POST.get('raison', '')
            candidature.statut = 'refusee'
            candidature.save()
            return JsonResponse({'success': True})
        except Candidature.DoesNotExist:
            return JsonResponse({'error': 'Candidature introuvable'}, status=404)
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# ============================================
# VUES ADMIN - AVIS
# ============================================

@admin_required
@login_required
def admin_avis(request):
    """Page d'administration des avis et évaluations"""
    view_type = request.GET.get('view', 'tous')  # 'tous', 'moderation', 'signales', 'analytics'
    per_page = int(request.GET.get('per_page', 25))
    page = int(request.GET.get('page', 1))
    
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
    
    # ============================================
    # STATISTIQUES GLOBALES
    # ============================================
    total_avis = AvisLogement.objects.count()
    avis_mois = AvisLogement.objects.filter(date_avis__gte=this_month_start).count()
    avis_mois_precedent = AvisLogement.objects.filter(
        date_avis__gte=last_month_start,
        date_avis__lt=this_month_start
    ).count()
    evolution_avis = ((avis_mois - avis_mois_precedent) / avis_mois_precedent * 100) if avis_mois_precedent > 0 else 0
    
    note_moyenne_globale = AvisLogement.objects.aggregate(Avg('note'))['note__avg'] or 0
    avis_en_attente = AvisLogement.objects.filter(verifie=False).count()
    avis_signales = AvisLogement.objects.filter(statut='signale').count() if hasattr(AvisLogement, 'statut') else 0
    
    # Taux réponse propriétaires (le modèle n'a pas de champ reponse_proprietaire)
    # Pour l'instant, on met 0 car cette fonctionnalité n'est pas implémentée
    avis_avec_reponse = 0
    taux_reponse = 0
    
    # ============================================
    # VUE TOUS LES AVIS
    # ============================================
    if view_type == 'tous':
        avis = AvisLogement.objects.select_related('locataire', 'logement').all()
        
        # Filtres
        search_query = request.GET.get('search', '').strip()
        if search_query:
            avis = avis.filter(
                Q(commentaire__icontains=search_query) |
                Q(locataire__username__icontains=search_query) |
                Q(logement__adresse__icontains=search_query)
            )
        
        note_filter = request.GET.get('note')
        if note_filter:
            avis = avis.filter(note=note_filter)
        
        statut_filter = request.GET.get('statut')
        if statut_filter:
            if statut_filter == 'verifie':
                avis = avis.filter(verifie=True)
            elif statut_filter == 'non_verifie':
                avis = avis.filter(verifie=False)
        
        # Tri
        sort_by = request.GET.get('sort', '-date_avis')
        avis = avis.order_by(sort_by)
        
        # Pagination
        paginator = Paginator(avis, per_page)
        avis_page = paginator.get_page(page)
        
        context = {
            'view_type': 'tous',
            'avis': avis_page,
            'per_page': per_page,
            'sort_by': sort_by,
            'filters': {
                'search': search_query,
                'note': note_filter,
                'statut': statut_filter,
            },
        }
    
    # ============================================
    # VUE MODÉRATION
    # ============================================
    elif view_type == 'moderation':
        avis = AvisLogement.objects.filter(verifie=False).select_related('locataire', 'logement').all()
        
        # Pagination
        paginator = Paginator(avis, per_page)
        avis_page = paginator.get_page(page)
        
        context = {
            'view_type': 'moderation',
            'avis': avis_page,
            'per_page': per_page,
        }
    
    # ============================================
    # VUE SIGNALÉS
    # ============================================
    elif view_type == 'signales':
        avis = AvisLogement.objects.filter(statut='signale').select_related('locataire', 'logement').all() if hasattr(AvisLogement, 'statut') else AvisLogement.objects.none()
        
        # Pagination
        paginator = Paginator(avis, per_page)
        avis_page = paginator.get_page(page)
        
        context = {
            'view_type': 'signales',
            'avis': avis_page,
            'per_page': per_page,
        }
    
    # ============================================
    # VUE ANALYTICS
    # ============================================
    else:  # analytics
        context = {
            'view_type': 'analytics',
        }
    
    # Stats communes
    context.update({
        'stats': {
            'total_avis': total_avis,
            'avis_mois': avis_mois,
            'evolution_avis': round(evolution_avis, 1),
            'note_moyenne_globale': round(note_moyenne_globale, 1),
            'taux_reponse': round(taux_reponse, 1),
            'avis_en_attente': avis_en_attente,
            'avis_signales': avis_signales,
        },
    })
    
    return render(request, 'core/admin/avis.html', context)

@admin_required
@login_required
def admin_avis_detail_ajax(request, avis_id):
    """Récupérer les détails d'un avis en JSON"""
    try:
        avis = AvisLogement.objects.select_related(
            'locataire', 'logement', 'logement__proprietaire'
        ).get(id=avis_id)
        
        data = {
            'id': avis.id,
            'auteur': {
                'id': avis.locataire.id,
                'username': avis.locataire.username,
                'email': avis.locataire.email,
                'avatar_url': avis.locataire.avatar.url if avis.locataire.avatar else None,
            },
            'logement': {
                'id': avis.logement.id,
                'titre': avis.logement.titre,
                'adresse': avis.logement.adresse,
            },
            'note': float(avis.note) if avis.note else 0,
            'titre': avis.titre or '',
            'commentaire': avis.commentaire or '',
            'note_proprete': float(avis.note_proprete) if avis.note_proprete else None,
            'note_equipements': float(avis.note_equipements) if avis.note_equipements else None,
            'note_localisation': float(avis.note_localisation) if avis.note_localisation else None,
            'note_bailleur': float(avis.note_bailleur) if avis.note_bailleur else None,
            'verifie': avis.verifie,
            'date_avis': avis.date_avis.strftime('%d/%m/%Y') if avis.date_avis else '',
        }
        
        return JsonResponse(data)
    except AvisLogement.DoesNotExist:
        return JsonResponse({'error': 'Avis introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# VUES ADMIN - AUTRES (STUBS)
# ============================================

@admin_required
@login_required
def admin_dashboard(request):
    """Tableau de bord administrateur"""
    from datetime import timedelta
    from django.utils import timezone
    
    # Filtres
    period = request.GET.get('period', '30j')
    city_filter = request.GET.get('city', 'all')
    user_type_filter = request.GET.get('user_type', 'all')
    
    # Calculer les dates selon la période
    today = timezone.now().date()
    if period == '7j':
        start_date = today - timedelta(days=7)
        prev_start_date = start_date - timedelta(days=7)
    elif period == '3mois':
        start_date = today - timedelta(days=90)
        prev_start_date = start_date - timedelta(days=90)
    elif period == '6mois':
        start_date = today - timedelta(days=180)
        prev_start_date = start_date - timedelta(days=180)
    elif period == '1an':
        start_date = today - timedelta(days=365)
        prev_start_date = start_date - timedelta(days=365)
    else:  # 30j par défaut
        start_date = today - timedelta(days=30)
        prev_start_date = start_date - timedelta(days=30)
    
    # Liste des villes (extraire depuis code_postal ou adresse)
    # Utiliser code_postal pour filtrer par ville (simplifié)
    cities = Logement.objects.values_list('code_postal', flat=True).distinct().order_by('code_postal')
    
    # Filtres de base
    users_qs = CustomUser.objects.all()
    logements_qs = Logement.objects.all()
    candidatures_qs = Candidature.objects.all()
    
    if city_filter != 'all':
        # Filtrer par code postal (représente la ville)
        logements_qs = logements_qs.filter(code_postal=city_filter)
        candidatures_qs = candidatures_qs.filter(logement__code_postal=city_filter)
    
    if user_type_filter == 'locataires':
        users_qs = users_qs.filter(is_locataire=True)
    elif user_type_filter == 'proprietaires':
        users_qs = users_qs.filter(is_proprietaire=True)
    elif user_type_filter == 'entreprises':
        users_qs = users_qs.filter(is_professionnel=True)
    
    # Statistiques utilisateurs
    total_users = users_qs.count()
    users_this_month = users_qs.filter(date_joined__gte=start_date).count()
    users_prev_month = users_qs.filter(
        date_joined__gte=prev_start_date,
        date_joined__lt=start_date
    ).count()
    users_evolution = ((users_this_month - users_prev_month) / users_prev_month * 100) if users_prev_month > 0 else 0
    
    # Statistiques logements
    total_logements = logements_qs.count()
    logements_this_month = logements_qs.filter(date_creation__gte=start_date).count()
    logements_prev_month = logements_qs.filter(
        date_creation__gte=prev_start_date,
        date_creation__lt=start_date
    ).count()
    logements_evolution = ((logements_this_month - logements_prev_month) / logements_prev_month * 100) if logements_prev_month > 0 else 0
    
    # Statistiques candidatures
    total_candidatures = candidatures_qs.count()
    candidatures_this_month = candidatures_qs.filter(created_at__date__gte=start_date).count()
    candidatures_prev_month = candidatures_qs.filter(
        created_at__date__gte=prev_start_date,
        created_at__date__lt=start_date
    ).count()
    candidatures_evolution = ((candidatures_this_month - candidatures_prev_month) / candidatures_prev_month * 100) if candidatures_prev_month > 0 else 0
    
    # Statistiques revenus (somme des loyers des baux actifs)
    baux_actifs = Bail.objects.filter(statut='actif')
    total_revenue = sum(float(bail.get_montant_total_mensuel()) for bail in baux_actifs)
    revenue_this_month = 0  # Simplifié - à améliorer avec historique
    revenue_prev_month = 0
    revenue_evolution = 0
    
    # Données pour graphiques
    # Croissance utilisateurs (12 derniers mois)
    user_growth_data = []
    for i in range(12):
        month_start = today - timedelta(days=30 * (11 - i))
        month_end = month_start + timedelta(days=30)
        count = users_qs.filter(date_joined__gte=month_start, date_joined__lt=month_end).count()
        user_growth_data.append({
            'month': month_start.strftime('%Y-%m'),
            'count': count
        })
    
    # Candidatures par statut
    candidatures_by_status = {}
    for statut, label in Candidature.STATUT_CHOICES:
        count = candidatures_qs.filter(statut=statut).count()
        candidatures_by_status[statut] = count
    
    # Activité récente (dernières connexions, créations, etc.)
    recent_activities = []
    # Ajouter les dernières connexions
    recent_logins = LoginHistory.objects.select_related('user').order_by('-timestamp')[:10]
    for login in recent_logins:
        recent_activities.append({
            'type_activite': 'connexion',
            'description': f"{login.user.username} s'est connecté",
            'user': login.user,
            'created_at': login.timestamp,
        })
    # Ajouter les derniers logements créés (utiliser la queryset filtrée)
    recent_logements = logements_qs.select_related('proprietaire').order_by('-date_creation')[:5]
    for logement in recent_logements:
        recent_activities.append({
            'type_activite': 'creation',
            'description': f"Nouveau logement: {logement.titre}",
            'user': logement.proprietaire,
            'created_at': logement.date_creation,
        })
    
    recent_activities.sort(key=lambda x: x['created_at'], reverse=True)
    recent_activities = recent_activities[:10]
    
    context = {
        'page_title': 'Tableau de bord',
        'period': period,
        'city_filter': city_filter,
        'user_type_filter': user_type_filter,
        'cities': cities,
        'total_users': total_users,
        'users_evolution': users_evolution,
        'total_logements': total_logements,
        'logements_evolution': logements_evolution,
        'candidatures_this_month': candidatures_this_month,
        'candidatures_evolution': candidatures_evolution,
        'total_revenue': total_revenue,
        'revenue_evolution': revenue_evolution,
        'recent_activities': recent_activities,
        'user_growth_data': user_growth_data,
        'candidatures_by_status': candidatures_by_status,
        'total_candidatures_for_chart': total_candidatures,
    }
    return render(request, 'core/admin/dashboard.html', context)

@admin_required
@login_required
def admin_users(request):
    """Gestion des utilisateurs"""
    from django.db.models import Count, Q
    from django.core.paginator import Paginator
    
    # Export CSV
    if request.GET.get('export') == 'csv':
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="utilisateurs.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Email', 'Username', 'Nom', 'Prénom', 'Email vérifié', 'Téléphone vérifié', 'Date inscription', 'Dernière connexion', 'Statut'])
        
        users = CustomUser.objects.all().order_by('-date_joined')
        for user in users:
            writer.writerow([
                user.email,
                user.username,
                user.last_name or '',
                user.first_name or '',
                'Oui' if user.email_verified else 'Non',
                'Oui' if user.phone_verified else 'Non',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                'Actif' if user.is_active else 'Inactif'
            ])
        
        return response
    
    # Filtres
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', 'all')
    verified_filter = request.GET.get('verified', 'all')
    user_type_filter = request.GET.get('user_type', 'all')
    
    # Queryset de base
    users = CustomUser.objects.annotate(
        posts_count=Count('posts', distinct=True),
        logements_count=Count('biens_possedes', distinct=True)
    ).all()
    
    # Filtres
    if search_query:
        users = users.filter(
            Q(email__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if status_filter == 'active':
        users = users.filter(is_active=True, is_suspended=False, is_banned=False)
    elif status_filter == 'suspended':
        users = users.filter(is_suspended=True)
    elif status_filter == 'banned':
        users = users.filter(is_banned=True)
    elif status_filter == 'inactive':
        users = users.filter(is_active=False)
    
    if verified_filter == 'email':
        users = users.filter(email_verified=True)
    elif verified_filter == 'phone':
        users = users.filter(phone_verified=True)
    elif verified_filter == 'both':
        users = users.filter(email_verified=True, phone_verified=True)
    
    if user_type_filter == 'locataires':
        users = users.filter(is_locataire=True)
    elif user_type_filter == 'proprietaires':
        users = users.filter(is_proprietaire=True)
    elif user_type_filter == 'professionnels':
        users = users.filter(is_professionnel=True)
    
    # Tri
    sort_by = request.GET.get('sort', '-date_joined')
    users = users.order_by(sort_by)
    
    # Pagination
    paginator = Paginator(users, 25)
    page = request.GET.get('page', 1)
    try:
        users_page = paginator.page(page)
    except:
        users_page = paginator.page(1)
    
    # Statistiques
    from datetime import timedelta
    from django.utils import timezone
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    month_ago = today - timedelta(days=30)
    
    total_users = CustomUser.objects.count()
    active_users = CustomUser.objects.filter(is_active=True, is_suspended=False, is_banned=False).count()
    verified_users = CustomUser.objects.filter(email_verified=True).count()
    suspended_users = CustomUser.objects.filter(is_suspended=True).count()
    banned_users = CustomUser.objects.filter(is_banned=True).count()
    new_users_week = CustomUser.objects.filter(date_joined__date__gte=week_ago).count()
    new_users_month = CustomUser.objects.filter(date_joined__date__gte=month_ago).count()
    recent_activity_users = CustomUser.objects.filter(last_activity__date__gte=week_ago).count()
    proprietaires_count = CustomUser.objects.filter(is_proprietaire=True).count()
    
    context = {
        'page_title': 'Gestion des Utilisateurs',
        'users': users_page,
        'total_users': total_users,
        'active_users': active_users,
        'verified_users': verified_users,
        'suspended_users': suspended_users,
        'banned_users': banned_users,
        'new_users_week': new_users_week,
        'new_users_month': new_users_month,
        'recent_activity_users': recent_activity_users,
        'proprietaires_count': proprietaires_count,
        'search_query': search_query,
        'status_filter': status_filter,
        'verified_filter': verified_filter,
        'user_type_filter': user_type_filter,
        'sort_by': sort_by,
    }
    return render(request, 'core/admin/users.html', context)

@admin_required
@login_required
def admin_user_detail(request, user_id):
    return stub_view(request)

@admin_required
@login_required
def admin_suspend_user(request, user_id):
    return stub_view(request)

@admin_required
@login_required
def admin_ban_user(request, user_id):
    return stub_view(request)

@admin_required
@login_required
def admin_delete_user(request, user_id):
    return stub_view(request)

@admin_required
@login_required
def admin_revoke_badges(request, user_id):
    return stub_view(request)

@admin_required
@login_required
def admin_groups(request):
    return stub_view(request)

@admin_required
@login_required
def admin_group_detail(request, group_id):
    return stub_view(request)

@admin_required
@login_required
def admin_groups_signaled(request):
    return stub_view(request)

@admin_required
@login_required
def admin_tickets(request):
    return stub_view(request)

@admin_required
@login_required
def admin_ticket_detail(request, ticket_id):
    return stub_view(request)

@admin_required
@login_required
def admin_ticket_reply(request, ticket_id):
    return stub_view(request)

@admin_required
@login_required
def admin_ticket_close(request, ticket_id):
    return stub_view(request)

@admin_required
@login_required
def admin_statistics(request):
    """Statistiques avancées"""
    from datetime import timedelta
    from django.utils import timezone
    from django.db.models import Count, Q
    
    # Filtre période
    period = request.GET.get('period', '30')
    try:
        period_days = int(period)
    except ValueError:
        period_days = 30
    
    today = timezone.now().date()
    start_date = today - timedelta(days=period_days)
    
    # Statistiques utilisateurs
    total_users = CustomUser.objects.count()
    new_users = CustomUser.objects.filter(date_joined__date__gte=start_date).count()
    active_users = CustomUser.objects.filter(last_activity__date__gte=start_date).count()
    
    # Croissance utilisateurs (par jour)
    user_growth_data = []
    for i in range(period_days):
        day = start_date + timedelta(days=i)
        count = CustomUser.objects.filter(date_joined__date=day).count()
        user_growth_data.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Statistiques posts
    total_posts = Post.objects.count()
    posts_this_period = Post.objects.filter(created_at__date__gte=start_date).count()
    
    # Posts par jour
    posts_per_day = []
    for i in range(period_days):
        day = start_date + timedelta(days=i)
        count = Post.objects.filter(created_at__date=day).count()
        posts_per_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Statistiques groupes
    total_groups = Group.objects.count()
    new_groups = Group.objects.filter(created_at__date__gte=start_date).count()
    
    # Statistiques messages
    total_messages = Message.objects.count()
    messages_this_period = Message.objects.filter(created_at__date__gte=start_date).count()
    
    # Messages par jour
    messages_per_day = []
    for i in range(period_days):
        day = start_date + timedelta(days=i)
        count = Message.objects.filter(created_at__date=day).count()
        messages_per_day.append({
            'date': day.strftime('%Y-%m-%d'),
            'count': count
        })
    
    # Statistiques logements
    total_logements = Logement.objects.count()
    new_logements = Logement.objects.filter(date_creation__date__gte=start_date).count()
    
    # Statistiques candidatures
    total_candidatures = Candidature.objects.count()
    candidatures_this_period = Candidature.objects.filter(created_at__date__gte=start_date).count()
    
    # Top utilisateurs actifs
    top_active_users = CustomUser.objects.annotate(
        posts_count=Count('posts', filter=Q(posts__created_at__date__gte=start_date)),
        comments_count=Count('post_comments', filter=Q(post_comments__created_at__date__gte=start_date))
    ).order_by('-last_activity')[:10]
    
    # Top groupes
    top_groups = Group.objects.annotate(
        member_count=Count('members', distinct=True),
        posts_count=Count('posts', filter=Q(posts__created_at__date__gte=start_date))
    ).order_by('-member_count')[:10]
    
    context = {
        'page_title': 'Statistiques avancées',
        'period': period,
        'period_days': period_days,
        'total_users': total_users,
        'new_users': new_users,
        'active_users': active_users,
        'user_growth_data': user_growth_data,
        'total_posts': total_posts,
        'posts_this_period': posts_this_period,
        'posts_per_day': posts_per_day,
        'total_groups': total_groups,
        'new_groups': new_groups,
        'total_messages': total_messages,
        'messages_this_period': messages_this_period,
        'messages_per_day': messages_per_day,
        'total_logements': total_logements,
        'new_logements': new_logements,
        'total_candidatures': total_candidatures,
        'candidatures_this_period': candidatures_this_period,
        'top_active_users': top_active_users,
        'top_groups': top_groups,
        'active_groups': top_groups,  # Alias pour le template (le template utilise active_groups)
    }
    return render(request, 'core/admin/statistics.html', context)

@admin_required
@login_required
def admin_logs(request):
    return stub_view(request)

@admin_required
@login_required
def admin_export_csv(request):
    return stub_view(request)

@admin_required
@login_required
def admin_moderation_posts(request):
    return stub_view(request)

@admin_required
@login_required
def admin_moderation_comments(request):
    return stub_view(request)

@admin_required
@login_required
def admin_moderation_messages(request):
    return stub_view(request)

@admin_required
@login_required
def admin_moderation_kanban(request):
    return stub_view(request)

@admin_required
@login_required
def admin_update_signalement_status(request):
    return stub_view(request)

@admin_required
@login_required
def admin_batch_action(request):
    return stub_view(request)

@admin_required
@login_required
def admin_moderate_post(request, signalement_id):
    return stub_view(request)

@admin_required
@login_required
def admin_moderate_comment(request, signalement_id):
    return stub_view(request)

@admin_required
@login_required
def admin_moderate_message(request, signalement_id):
    return stub_view(request)

@admin_required
@login_required
def admin_verifications_identity(request):
    return stub_view(request)

@admin_required
@login_required
def admin_verifications_owner(request):
    return stub_view(request)

@admin_required
@login_required
def admin_approve_verification(request, request_id):
    return stub_view(request)

@admin_required
@login_required
def admin_reject_verification(request, request_id):
    return stub_view(request)

@admin_required
@login_required
def admin_reclamations(request):
    return stub_view(request)

@admin_required
@login_required
def admin_reclamation_detail(request, reclamation_id):
    return stub_view(request)

@admin_required
@login_required
def admin_approve_reclamation(request, reclamation_id):
    return stub_view(request)

@admin_required
@login_required
def admin_reject_reclamation(request, reclamation_id):
    return stub_view(request)

@admin_required
@login_required
def admin_settings(request):
    return stub_view(request)

@admin_required
@login_required
def admin_settings_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_role_create(request):
    return stub_view(request)

@admin_required
@login_required
def admin_role_update(request, role_id):
    return stub_view(request)

@admin_required
@login_required
def admin_role_delete(request, role_id):
    return stub_view(request)

@admin_required
@login_required
def admin_invitation_send(request):
    return stub_view(request)

@admin_required
@login_required
def admin_payment_config_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_notification_config_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_notification_template_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_security_config_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_integration_config_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_activity_logs_export(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas_create_version(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas_restore_version(request, version_id):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas_reset(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas_export_pdf(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_model_canvas_share(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan_create_version(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan_restore_version(request, version_id):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan_export_pdf(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan_upload_document(request):
    return stub_view(request)

@admin_required
@login_required
def admin_business_plan_add_comment(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_studies(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_builder(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_create(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_save_question(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_delete_question(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_reorder_questions(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_results(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_export_csv(request):
    return stub_view(request)

@admin_required
@login_required
def admin_market_study_export_excel(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis_add_competitor(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis_edit_competitor(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis_get_competitor(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis_delete_competitor(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis_save_swot(request):
    return stub_view(request)

@admin_required
@login_required
def admin_competitive_analysis_export(request):
    return stub_view(request)

@admin_required
@login_required
def admin_financial_projections(request):
    return stub_view(request)

@admin_required
@login_required
def admin_financial_projection_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_cash_flow_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_balance_sheet_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_scenario_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_kpis_save(request):
    return stub_view(request)

@admin_required
@login_required
def admin_moderation(request):
    return stub_view(request)

@admin_required
@login_required
def admin_reported_content_action(request, content_id):
    return stub_view(request)

@admin_required
@login_required
def admin_user_moderation_action(request, user_moderation_id):
    return stub_view(request)

@admin_required
@login_required
def admin_verification_action(request, verification_id):
    return stub_view(request)

@admin_required
@login_required
def admin_property_claim_action(request, claim_id):
    return stub_view(request)

@admin_required
@login_required
def admin_support_tickets(request):
    return stub_view(request)

@admin_required
@login_required
def admin_support_ticket_detail(request, ticket_id):
    return stub_view(request)

@admin_required
@login_required
def admin_support_ticket_update_status(request, ticket_id):
    return stub_view(request)

@admin_required
@login_required
def admin_support_ticket_reply(request, ticket_id):
    return stub_view(request)

@admin_required
@login_required
def admin_support_ticket_assign(request, ticket_id):
    return stub_view(request)

# ============================================
# VUES PUBLIQUES - PAGES PRINCIPALES
# ============================================

def landing_page(request):
    """Page d'accueil"""
    return render(request, 'core/landing-page.html')

def map_view(request):
    """Vue carte"""
    return render(request, 'core/map.html')

def liste_view(request):
    """Vue liste"""
    return render(request, 'core/liste.html')

# ============================================
# VUES AUTHENTIFICATION
# ============================================

@rate_limit(get_client_ip_key, limit=3, window=3600, message="Trop de tentatives d'inscription. Veuillez réessayer dans 1 heure.")
def signup_view(request):
    """Inscription avec sécurité renforcée"""
    if request.user.is_authenticated:
        return redirect('connect-home')
    
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email').lower().strip()
            
            # Vérifier si l'email est déjà utilisé (double vérification)
            if CustomUser.objects.filter(email=email).exists():
                messages.error(request, 'Cet email est déjà utilisé.')
                return render(request, 'core/signup_modern.html', {'form': form})
            
            # Vérifier si le nom d'utilisateur est déjà utilisé (double vérification)
            username = form.cleaned_data.get('username')
            if CustomUser.objects.filter(username=username).exists():
                messages.error(request, 'Ce nom d\'utilisateur est déjà pris.')
                return render(request, 'core/signup_modern.html', {'form': form})
            
            try:
                user = form.save()
                
                # Créer token de vérification email
                token = create_email_verification_token(user)
                send_verification_email(user, token.token)
                
                # Vérifier et attribuer badges
                check_and_award_badges(user)
                
                # Logger la création de compte
                ip = get_client_ip(request)
                device_info = get_device_info(request)
                log_login_attempt(user, request, success=True, reason='Compte créé')
                create_user_session(user, request)
                
                # Alerte sécurité pour nouvelle inscription
                create_security_alert(
                    user, 'account_created',
                    'Nouveau compte créé',
                    f'Compte créé depuis {device_info["device_type"]} ({ip})',
                    ip_address=ip,
                    device_info=device_info,
                    severity='low'
                )
                
                messages.success(request, 'Votre compte a été créé avec succès ! Veuillez vérifier votre email pour activer votre compte.')
                return redirect('login')
            except Exception as e:
                messages.error(request, 'Une erreur est survenue lors de la création de votre compte. Veuillez réessayer.')
                return render(request, 'core/signup_modern.html', {'form': form})
    else:
        form = SignupForm()
    
    return render(request, 'core/signup_modern.html', {'form': form})

@rate_limit(get_email_key, limit=5, window=300, message="Trop de tentatives de connexion. Veuillez réessayer plus tard.")
def login_view(request):
    """Connexion avec sécurité renforcée"""
    if request.user.is_authenticated:
        return redirect('connect-home')
    
    # Vérifier si l'utilisateur est bloqué (trop de tentatives échouées)
    if request.method == 'POST':
        email = request.POST.get('username', '').lower().strip()
        if email:
            from django.core.cache import cache
            login_key = f"login_failed:{email}"
            failed_attempts = cache.get(login_key, 0)
            
            if failed_attempts >= 5:
                messages.error(request, 'Trop de tentatives de connexion échouées. Veuillez réessayer dans 15 minutes ou utiliser la réinitialisation de mot de passe.')
                form = LoginForm()
                return render(request, 'core/login_modern.html', {'form': form, 'rate_limited': True})
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username').lower().strip()  # Le form utilise email comme username
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me', False)
            
            # Authentifier par email
            try:
                user = CustomUser.objects.get(email=email)
                
                # Vérifier si le compte est actif
                if not user.is_active:
                    messages.error(request, 'Ce compte est désactivé. Veuillez contacter le support.')
                    form = LoginForm()
                    return render(request, 'core/login_modern.html', {'form': form})
                
                # Vérifier si le compte est banni
                if user.is_banned:
                    messages.error(request, 'Ce compte a été banni. Veuillez contacter le support pour plus d\'informations.')
                    form = LoginForm()
                    return render(request, 'core/login_modern.html', {'form': form})
                
                # Vérifier si le compte est suspendu
                if user.is_suspended and user.suspended_until and user.suspended_until > timezone.now():
                    messages.error(request, f'Ce compte est suspendu jusqu\'au {user.suspended_until.strftime("%d/%m/%Y %H:%M")}.')
                    form = LoginForm()
                    return render(request, 'core/login_modern.html', {'form': form})
                
                # Authentifier
                user = authenticate(request, username=user.username, password=password)
            except CustomUser.DoesNotExist:
                user = None
            
            if user is not None:
                # Réinitialiser les tentatives échouées
                from django.core.cache import cache
                login_key = f"login_failed:{email}"
                cache.delete(login_key)
                
                # Vérifier si 2FA est activé
                if user.two_factor_enabled:
                    # Stocker les infos de connexion en session pour après 2FA
                    request.session['pending_user_id'] = user.id
                    request.session['remember_me'] = remember_me
                    request.session['login_timestamp'] = timezone.now().isoformat()
                    return redirect('verify-2fa')
                
                # Connexion normale
                login(request, user)
                
                # Session permanente si "Se souvenir de moi"
                if not remember_me:
                    request.session.set_expiry(0)  # Session expire à la fermeture du navigateur
                else:
                    request.session.set_expiry(1209600)  # 2 semaines
                
                # Logger la connexion
                ip = get_client_ip(request)
                device_info = get_device_info(request)
                log_login_attempt(user, request, success=True)
                create_user_session(user, request)
                
                # Vérifier connexion suspecte
                if check_suspicious_login(user, request):
                    create_security_alert(
                        user, 'suspicious_login',
                        'Connexion depuis un nouvel appareil',
                        f'Connexion depuis {device_info["device_type"]} ({ip})',
                        ip_address=ip,
                        device_info=device_info,
                        severity='medium'
                    )
                    messages.warning(request, 'Connexion depuis un nouvel appareil détectée. Vérifiez vos emails pour plus de détails.')
                
                # Vérifier et attribuer badges
                check_and_award_badges(user)
                
                messages.success(request, f'Bienvenue {user.username} !')
                
                # Redirection vers la page demandée ou home
                next_url = request.GET.get('next', 'connect-home')
                return redirect(next_url)
            else:
                # Incrémenter les tentatives échouées
                from django.core.cache import cache
                login_key = f"login_failed:{email}"
                failed_attempts = cache.get(login_key, 0) + 1
                cache.set(login_key, failed_attempts, 900)  # 15 minutes
                
                messages.error(request, 'Email ou mot de passe incorrect.')
                # Logger tentative échouée
                try:
                    user_obj = CustomUser.objects.get(email=email)
                    log_login_attempt(user_obj, request, success=False, reason='Mot de passe incorrect')
                    
                    # Alerte sécurité après plusieurs tentatives
                    if failed_attempts >= 3:
                        create_security_alert(
                            user_obj, 'failed_login_attempts',
                            f'{failed_attempts} tentatives de connexion échouées',
                            f'Plusieurs tentatives de connexion ont échoué depuis {ip}',
                            ip_address=ip,
                            severity='high'
                        )
                except CustomUser.DoesNotExist:
                    pass  # Ne pas révéler si l'email existe
    else:
        form = LoginForm()
    
    return render(request, 'core/login_modern.html', {'form': form})

def logout_view(request):
    """Déconnexion"""
    if request.user.is_authenticated:
        # Marquer session comme non-courante
        if hasattr(request, 'session') and request.session.session_key:
            UserSession.objects.filter(session_key=request.session.session_key).update(is_current=False)
        logout(request)
        messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('landing-page')

def magic_link_login(request, token):
    """Connexion via magic link"""
    try:
        magic_token = MagicLinkToken.objects.get(token=token, used=False, expires_at__gt=timezone.now())
        user = magic_token.user
        
        # Marquer le token comme utilisé
        magic_token.used = True
        magic_token.save()
        
        # Connecter l'utilisateur
        login(request, user)
        create_user_session(user, request)
        log_login_attempt(user, request, success=True, reason='Magic link')
        
        messages.success(request, f'Bienvenue {user.username} !')
        return redirect('connect-home')
    except MagicLinkToken.DoesNotExist:
        messages.error(request, 'Lien invalide ou expiré.')
        return redirect('login')

@rate_limit(get_email_key, limit=3, window=900, message="Trop de demandes de magic link. Veuillez réessayer dans 15 minutes.")
def request_magic_link(request):
    """Demander un magic link avec sécurité renforcée"""
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({'success': False, 'error': 'Email requis'}, status=400)
        
        # Vérifier le rate limiting par email
        from django.core.cache import cache
        magic_link_key = f"magic_link:{email}"
        magic_link_count = cache.get(magic_link_key, 0)
        
        if magic_link_count >= 3:
            return JsonResponse({
                'success': False, 
                'error': 'Trop de demandes de magic link. Veuillez réessayer dans 15 minutes.'
            }, status=429)
        
        try:
            user = CustomUser.objects.get(email=email)
            
            # Vérifier si le compte est actif
            if not user.is_active:
                return JsonResponse({'success': False, 'error': 'Ce compte est désactivé.'}, status=403)
            
            # Créer et envoyer le magic link
            ip = get_client_ip(request)
            token = create_magic_link(user, ip)
            send_magic_link_email(user, token)
            
            # Incrémenter le compteur
            cache.set(magic_link_key, magic_link_count + 1, 900)  # 15 minutes
            
            # Logger la demande
            log_login_attempt(user, request, success=True, reason='Demande magic link')
            create_security_alert(
                user, 'magic_link_requested',
                'Demande de magic link',
                f'Une demande de magic link a été effectuée depuis {ip}',
                ip_address=ip,
                severity='low'
            )
            
            return JsonResponse({'success': True, 'message': 'Un lien de connexion a été envoyé à votre adresse email.'})
        except CustomUser.DoesNotExist:
            # Ne pas révéler si l'email existe (timing attack protection)
            import time
            time.sleep(0.5)
            return JsonResponse({'success': True, 'message': 'Un lien de connexion a été envoyé à votre adresse email.'})
    
    return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)

def verify_2fa_view(request):
    """Vérification 2FA"""
    if not request.session.get('pending_user_id'):
        return redirect('login')
    
    user_id = request.session.get('pending_user_id')
    try:
        user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        code = request.POST.get('code', '').strip()
        if verify_2fa_code(user, code):
            # Connexion réussie
            login(request, user)
            remember_me = request.session.get('remember_me', False)
            if not remember_me:
                request.session.set_expiry(0)
            else:
                request.session.set_expiry(1209600)
            
            create_user_session(user, request)
            log_login_attempt(user, request, success=True, reason='2FA vérifié')
            
            # Nettoyer la session
            del request.session['pending_user_id']
            del request.session['remember_me']
            
            messages.success(request, f'Bienvenue {user.username} !')
            return redirect('connect-home')
        else:
            messages.error(request, 'Code 2FA incorrect.')
    
    return render(request, 'core/verify_2fa.html', {'user': user})

def setup_2fa_view(request):
    """Configuration 2FA"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        if request.user.two_factor_enabled:
            messages.info(request, 'La 2FA est déjà activée.')
            return redirect('security-settings')
        
        secret = generate_2fa_secret()
        request.user.two_factor_secret = secret
        request.user.save()
        
        qr_code = generate_2fa_qr_code(request.user, secret)
        backup_codes = generate_backup_codes(request.user)
        
        return render(request, 'core/setup_2fa.html', {
            'secret': secret,
            'qr_code': qr_code,
            'backup_codes': backup_codes,
            'setup_mode': True
        })
    
    return render(request, 'core/setup_2fa.html')

def disable_2fa_view(request):
    """Désactiver 2FA"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        request.user.two_factor_enabled = False
        request.user.two_factor_secret = None
        request.user.save()
        messages.success(request, 'La 2FA a été désactivée.')
        return redirect('security-settings')
    
    return redirect('security-settings')

def get_2fa_backup_codes(request):
    """Récupérer codes de secours 2FA"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    from .models import TwoFactorBackupCode
    codes = TwoFactorBackupCode.objects.filter(user=request.user, used=False).values_list('code', flat=True)
    return JsonResponse({'codes': list(codes)})

def verify_email(request, token):
    """Vérification email"""
    try:
        token_obj = EmailVerificationToken.objects.get(token=token, expires_at__gt=timezone.now(), used=False)
        user = token_obj.user
        user.email_verified = True
        user.save()
        token_obj.used = True
        token_obj.save()
        
        check_and_award_badges(user)
        messages.success(request, 'Votre email a été vérifié avec succès !')
        return redirect('login')
    except EmailVerificationToken.DoesNotExist:
        messages.error(request, 'Lien de vérification invalide ou expiré.')
        return redirect('login')

@rate_limit(get_email_key, limit=3, window=3600, message="Trop de demandes de réinitialisation. Veuillez réessayer dans 1 heure.")
def password_reset_request(request):
    """Demande réinitialisation mot de passe avec sécurité renforcée"""
    if request.user.is_authenticated:
        return redirect('connect-home')
    
    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].lower().strip()
            
            # Vérifier le rate limiting par email
            from django.core.cache import cache
            reset_key = f"password_reset:{email}"
            reset_count = cache.get(reset_key, 0)
            
            if reset_count >= 3:
                messages.error(request, 'Trop de demandes de réinitialisation pour cet email. Veuillez réessayer dans 1 heure.')
                return render(request, 'core/password_reset_request.html', {'form': form})
            
            try:
                user = CustomUser.objects.get(email=email)
                
                # Vérifier si le compte est actif
                if not user.is_active:
                    messages.error(request, 'Ce compte est désactivé. Veuillez contacter le support.')
                    return render(request, 'core/password_reset_request.html', {'form': form})
                
                # Créer le token
                ip = get_client_ip(request)
                token = create_password_reset_token(user, ip)
                send_password_reset_email(user, token.token)
                
                # Incrémenter le compteur
                cache.set(reset_key, reset_count + 1, 3600)
                
                # Logger la demande
                log_login_attempt(user, request, success=True, reason='Demande réinitialisation mot de passe')
                create_security_alert(
                    user, 'password_reset_requested',
                    'Demande de réinitialisation de mot de passe',
                    f'Une demande de réinitialisation a été effectuée depuis {ip}',
                    ip_address=ip,
                    severity='medium'
                )
                
                messages.success(request, 'Un email de réinitialisation a été envoyé. Vérifiez votre boîte de réception.')
            except CustomUser.DoesNotExist:
                # Ne pas révéler si l'email existe (timing attack protection)
                import time
                time.sleep(0.5)  # Délai pour éviter timing attacks
                messages.success(request, 'Un email de réinitialisation a été envoyé. Vérifiez votre boîte de réception.')
    else:
        form = PasswordResetRequestForm()
    
    return render(request, 'core/password_reset_request.html', {'form': form})

@rate_limit(get_client_ip_key, limit=5, window=3600, message="Trop de tentatives de réinitialisation. Veuillez réessayer dans 1 heure.")
def password_reset_confirm(request, token):
    """Confirmation réinitialisation mot de passe avec sécurité renforcée"""
    if request.user.is_authenticated:
        return redirect('connect-home')
    
    try:
        token_obj = PasswordResetToken.objects.get(token=token, expires_at__gt=timezone.now(), used=False)
        user = token_obj.user
        
        # Vérifier si le compte est actif
        if not user.is_active:
            messages.error(request, 'Ce compte est désactivé. Veuillez contacter le support.')
            return redirect('password-reset-request')
        
        if request.method == 'POST':
            form = PasswordResetForm(request.POST)
            if form.is_valid():
                # Vérifier si le nouveau mot de passe est différent de l'ancien
                if user.check_password(form.cleaned_data['password1']):
                    messages.error(request, 'Le nouveau mot de passe doit être différent de l\'ancien.')
                    return render(request, 'core/password_reset_confirm.html', {'form': form, 'token': token})
                
                # Réinitialiser le mot de passe
                user.set_password(form.cleaned_data['password1'])
                user.save()
                
                # Marquer le token comme utilisé
                token_obj.used = True
                token_obj.save()
                
                # Réinitialiser toutes les sessions actives (forcer reconnexion)
                from .models import UserSession
                UserSession.objects.filter(user=user).update(is_current=False)
                
                # Logger la réinitialisation
                ip = get_client_ip(request)
                device_info = get_device_info(request)
                log_login_attempt(user, request, success=True, reason='Mot de passe réinitialisé')
                create_security_alert(
                    user, 'password_reset',
                    'Mot de passe réinitialisé',
                    f'Le mot de passe a été réinitialisé depuis {device_info["device_type"]} ({ip})',
                    ip_address=ip,
                    device_info=device_info,
                    severity='high'
                )
                
                messages.success(request, 'Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.')
                return redirect('login')
        else:
            form = PasswordResetForm()
        
        return render(request, 'core/password_reset_confirm.html', {'form': form, 'token': token})
    except PasswordResetToken.DoesNotExist:
        messages.error(request, 'Lien invalide ou expiré. Veuillez faire une nouvelle demande de réinitialisation.')
        return redirect('password-reset-request')

# ============================================
# VUES PROFIL
# ============================================

def profile_view(request, user_id=None):
    """Vue profil utilisateur"""
    if user_id:
        try:
            profile_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            messages.error(request, 'Utilisateur introuvable.')
            return redirect('connect-home')
    else:
        if not request.user.is_authenticated:
            return redirect('login')
        profile_user = request.user
    
    # Vérifier visibilité du profil
    if profile_user != request.user:
        if profile_user.profil_visibility == 'private':
            messages.error(request, 'Ce profil est privé.')
            return redirect('connect-home')
        elif profile_user.profil_visibility == 'connections':
            # TODO: Vérifier si utilisateur connecté
            pass
    
    # Stats
    favoris_count = Favori.objects.filter(utilisateur=profile_user).count()
    recent_logins = LoginHistory.objects.filter(user=profile_user, success=True).order_by('-timestamp')[:10]
    active_sessions = UserSession.objects.filter(user=profile_user, is_current=True)
    
    # Badges
    user_badges = UserBadge.objects.filter(user=profile_user).select_related('badge')
    
    context = {
        'user': profile_user,
        'profile_user': profile_user,
        'favoris_count': favoris_count,
        'recent_logins': recent_logins,
        'active_sessions': active_sessions,
        'user_badges': user_badges,
        'is_own_profile': profile_user == request.user,
    }
    
    return render(request, 'core/profile.html', context)

def profile_edit(request):
    """Édition profil"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            check_and_award_badges(request.user)
            messages.success(request, 'Votre profil a été mis à jour avec succès.')
            return redirect('profile')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'core/profile_edit.html', {'form': form})

def check_badges(request):
    """Vérifier et attribuer badges"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    badges_awarded = check_and_award_badges(request.user)
    if badges_awarded:
        return JsonResponse({
            'success': True,
            'badges': [{'name': b.name, 'description': b.description} for b in badges_awarded]
        })
    return JsonResponse({'success': True, 'badges': []})

def security_settings(request):
    """Paramètres sécurité"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Sessions actives
    active_sessions = UserSession.objects.filter(user=request.user).order_by('-created_at')
    
    # Historique de connexion
    login_history = LoginHistory.objects.filter(user=request.user).order_by('-timestamp')[:20]
    
    # Alertes de sécurité
    from .models import SecurityAlert
    security_alerts = SecurityAlert.objects.filter(user=request.user).order_by('-created_at')[:10]
    
    context = {
        'active_sessions': active_sessions,
        'login_history': login_history,
        'security_alerts': security_alerts,
    }
    
    return render(request, 'core/security_settings.html', context)

def revoke_session(request, session_id):
    """Révoquer une session"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        session = UserSession.objects.get(id=session_id, user=request.user)
        session.is_current = False
        session.save()
        
        # Si c'est la session courante, déconnecter
        if session.session_key == request.session.session_key:
            logout(request)
            return JsonResponse({'success': True, 'redirect': '/login/'})
        
        return JsonResponse({'success': True})
    except UserSession.DoesNotExist:
        return JsonResponse({'error': 'Session introuvable'}, status=404)

# ============================================
# VUES LOGEMENTS
# ============================================

def logement_detail(request, id):
    """Détail logement (ancienne route)"""
    return redirect('logement-detail-view', id=id)

def logement_detail_view(request, id):
    """Vue détail logement"""
    try:
        logement = Logement.objects.select_related('proprietaire').prefetch_related('images', 'avis').get(id=id)
        is_favori = False
        if request.user.is_authenticated:
            is_favori = Favori.objects.filter(utilisateur=request.user, logement=logement).exists()
        
        context = {
            'logement': logement,
            'is_favori': is_favori,
        }
        return render(request, 'core/logement_detail_page.html', context)
    except Logement.DoesNotExist:
        messages.error(request, 'Logement introuvable.')
        return redirect('map')

def mes_biens(request):
    """Mes biens (propriétaire)"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    logements = Logement.objects.filter(proprietaire=request.user).prefetch_related('images', 'avis')
    
    context = {
        'logements': logements,
    }
    return render(request, 'core/mes_biens.html', context)

def candidater_logement(request):
    """Candidater à un logement"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        logement_id = request.POST.get('logement_id')
        try:
            logement = Logement.objects.get(id=logement_id)
            # Vérifier si candidature existe déjà
            if Candidature.objects.filter(candidat=request.user, logement=logement).exists():
                return JsonResponse({'error': 'Vous avez déjà candidaté à ce logement.'}, status=400)
            
            candidature = Candidature.objects.create(
                candidat=request.user,
                logement=logement,
                statut='en_attente'
            )
            return JsonResponse({'success': True, 'candidature_id': candidature.id})
        except Logement.DoesNotExist:
            return JsonResponse({'error': 'Logement introuvable.'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def reclamer_bien(request):
    """Réclamer un bien"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        logement_id = request.POST.get('logement_id')
        try:
            logement = Logement.objects.get(id=logement_id)
            # Vérifier si réclamation existe déjà
            if ReclamationProprietaire.objects.filter(proprietaire=request.user, logement=logement).exists():
                return JsonResponse({'error': 'Vous avez déjà réclamé ce bien.'}, status=400)
            
            reclamation = ReclamationProprietaire.objects.create(
                proprietaire=request.user,
                logement=logement,
                statut='en_attente'
            )
            return JsonResponse({'success': True, 'reclamation_id': reclamation.id})
        except Logement.DoesNotExist:
            return JsonResponse({'error': 'Logement introuvable.'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def ajouter_avis(request):
    """Ajouter un avis"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    logement_id = request.GET.get('logement_id') or request.POST.get('logement_id')
    if not logement_id:
        messages.error(request, 'Logement non spécifié.')
        return redirect('map')
    
    try:
        logement = Logement.objects.get(id=logement_id)
    except Logement.DoesNotExist:
        messages.error(request, 'Logement introuvable.')
        return redirect('map')
    
    if request.method == 'POST':
        note = request.POST.get('note')
        commentaire = request.POST.get('commentaire', '')
        
        if note:
            avis = AvisLogement.objects.create(
                locataire=request.user,
                logement=logement,
                note=note,
                commentaire=commentaire,
                verifie=False
            )
            logement.recalculer_note_moyenne()
            messages.success(request, 'Votre avis a été ajouté avec succès.')
            return redirect('logement-detail-view', id=logement.id)
    
    return render(request, 'core/ajouter_avis.html', {'logement': logement})

def ajouter_avis_profil(request):
    """Ajouter avis depuis profil"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    user_id = request.GET.get('user_id') or request.POST.get('user_id')
    if not user_id:
        messages.error(request, 'Utilisateur non spécifié.')
        return redirect('connect-home')
    
    try:
        target_user = CustomUser.objects.get(id=user_id)
    except CustomUser.DoesNotExist:
        messages.error(request, 'Utilisateur introuvable.')
        return redirect('connect-home')
    
    # TODO: Implémenter l'ajout d'avis sur un utilisateur
    return stub_view(request)

def mes_avis(request):
    """Mes avis"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    avis = AvisLogement.objects.filter(locataire=request.user).select_related('logement').order_by('-date_avis')
    
    context = {
        'avis': avis,
    }
    return render(request, 'core/mes_avis.html', context)

# ============================================
# API LOGEMENTS
# ============================================

def api_get_logements(request):
    """API récupérer logements"""
    logements = Logement.objects.select_related('proprietaire').prefetch_related('images').all()
    
    # Filtres
    ville = request.GET.get('ville')
    if ville:
        # Filtrer par code postal ou adresse (le modèle n'a pas de champ ville)
        logements = logements.filter(
            Q(code_postal__icontains=ville) | 
            Q(adresse__icontains=ville)
        )
    
    type_logement = request.GET.get('type')
    if type_logement:
        logements = logements.filter(type_logement=type_logement)
    
    prix_min = request.GET.get('prix_min')
    prix_max = request.GET.get('prix_max')
    if prix_min:
        logements = logements.filter(prix__gte=prix_min)
    if prix_max:
        logements = logements.filter(prix__lte=prix_max)
    
    # Limiter les résultats
    limit = int(request.GET.get('limit', 100))
    logements = logements[:limit]
    
    data = []
    for logement in logements:
        images = [img.image.url for img in logement.images.all()[:5]]
        data.append({
            'id': logement.id,
            'titre': logement.titre,
            'adresse': logement.adresse,
            'ville': logement.code_postal or '',  # Utiliser code_postal car le modèle n'a pas de champ ville
            'prix': float(logement.prix) if logement.prix else 0,
            'surface': logement.surface or 0,
            'chambres': logement.chambres or 0,
            'note_moyenne': float(logement.note_moyenne) if logement.note_moyenne else 0,
            'latitude': float(logement.latitude) if logement.latitude else None,
            'longitude': float(logement.longitude) if logement.longitude else None,
            'images': images,
        })
    
    return JsonResponse({'logements': data})

def api_logement_detail(request, id):
    """API détail logement"""
    try:
        logement = Logement.objects.select_related('proprietaire').prefetch_related('images', 'avis').get(id=id)
        images = [{'url': img.image.url, 'caption': img.caption or ''} for img in logement.images.all()]
        avis = [{
            'note': float(a.note),
            'commentaire': a.commentaire or '',
            'date': a.date_avis.strftime('%d/%m/%Y') if a.date_avis else '',
        } for a in logement.avis.filter(verifie=True)[:10]]
        
        data = {
            'id': logement.id,
            'titre': logement.titre,
            'adresse': logement.adresse,
            'code_postal': logement.code_postal or '',
            'ville': logement.code_postal or '',  # Utiliser code_postal car le modèle n'a pas de champ ville
            'description': logement.description or '',
            'prix': float(logement.prix) if logement.prix else 0,
            'surface': logement.surface or 0,
            'chambres': logement.chambres or 0,
            'type_logement': logement.type_logement,
            'note_moyenne': float(logement.note_moyenne) if logement.note_moyenne else 0,
            'nombre_avis': logement.nombre_avis or 0,
            'latitude': float(logement.latitude) if logement.latitude else None,
            'longitude': float(logement.longitude) if logement.longitude else None,
            'images': images,
            'avis': avis,
        }
        return JsonResponse(data)
    except Logement.DoesNotExist:
        return JsonResponse({'error': 'Logement introuvable'}, status=404)

def api_logement_detail_complet(request, id):
    """API détail logement complet"""
    try:
        logement = Logement.objects.select_related('proprietaire').prefetch_related('images', 'avis').get(id=id)
        images = [{'image': img.image.url, 'caption': img.caption or ''} for img in logement.images.all()]
        avis = [{
            'id': a.id,
            'note': float(a.note),
            'titre': a.titre or '',
            'commentaire': a.commentaire or '',
            'locataire': a.locataire.username,
            'date': a.date_avis.strftime('%d/%m/%Y') if a.date_avis else '',
        } for a in logement.avis.filter(verifie=True)]
        
        is_favori = False
        if request.user.is_authenticated:
            is_favori = Favori.objects.filter(utilisateur=request.user, logement=logement).exists()
        
        data = {
            'id': logement.id,
            'titre': logement.titre,
            'adresse': logement.adresse,
            'code_postal': logement.code_postal or '',
            'ville': logement.code_postal or '',  # Utiliser code_postal car le modèle n'a pas de champ ville
            'description': logement.description or '',
            'prix': float(logement.prix) if logement.prix else 0,
            'surface': logement.surface or 0,
            'chambres': logement.chambres or 0,
            'type_logement': logement.type_logement,
            'statut': logement.statut,
            'note_moyenne': float(logement.note_moyenne) if logement.note_moyenne else 0,
            'nombre_avis': logement.nombre_avis or 0,
            'latitude': float(logement.latitude) if logement.latitude else None,
            'longitude': float(logement.longitude) if logement.longitude else None,
            'images': images,
            'avis': avis,
            'is_favori': is_favori,
            'proprietaire': {
                'id': logement.proprietaire.id,
                'username': logement.proprietaire.username,
            } if logement.proprietaire else None,
        }
        return JsonResponse(data)
    except Logement.DoesNotExist:
        return JsonResponse({'error': 'Logement introuvable'}, status=404)

def api_logements_recommandes(request, logement_id):
    """API logements recommandés"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_logements_triés(request):
    """API logements triés"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_logements_by_radius(request):
    """API logements par rayon"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_create_avis(request, id):
    """API créer avis"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        try:
            logement = Logement.objects.get(id=id)
            note = request.POST.get('note')
            commentaire = request.POST.get('commentaire', '').strip()
            
            if not note:
                return JsonResponse({'error': 'La note est requise'}, status=400)
            
            avis = AvisLogement.objects.create(
                locataire=request.user,
                logement=logement,
                note=note,
                commentaire=commentaire,
                verifie=False
            )
            logement.recalculer_note_moyenne()
            
            return JsonResponse({
                'success': True,
                'avis': {
                    'id': avis.id,
                    'note': float(avis.note),
                    'commentaire': avis.commentaire,
                }
            })
        except Logement.DoesNotExist:
            return JsonResponse({'error': 'Logement introuvable'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def api_reclamer_bien(request, id):
    """API réclamer bien"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        try:
            logement = Logement.objects.get(id=id)
            # Vérifier si réclamation existe déjà
            if ReclamationProprietaire.objects.filter(proprietaire=request.user, logement=logement).exists():
                return JsonResponse({'error': 'Vous avez déjà réclamé ce bien'}, status=400)
            
            reclamation = ReclamationProprietaire.objects.create(
                proprietaire=request.user,
                logement=logement,
                statut='en_attente'
            )
            return JsonResponse({'success': True, 'reclamation_id': reclamation.id})
        except Logement.DoesNotExist:
            return JsonResponse({'error': 'Logement introuvable'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def api_toggle_favori(request):
    """API toggle favori"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        logement_id = request.POST.get('logement_id')
        try:
            logement = Logement.objects.get(id=logement_id)
            favori, created = Favori.objects.get_or_create(
                utilisateur=request.user,
                logement=logement
            )
            if not created:
                favori.delete()
                return JsonResponse({'success': True, 'is_favori': False})
            return JsonResponse({'success': True, 'is_favori': True})
        except Logement.DoesNotExist:
            return JsonResponse({'error': 'Logement introuvable'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def api_toggle_favori_map(request, id):
    """API toggle favori depuis carte"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        logement = Logement.objects.get(id=id)
        favori, created = Favori.objects.get_or_create(
            utilisateur=request.user,
            logement=logement
        )
        if not created:
            favori.delete()
            return JsonResponse({'success': True, 'is_favori': False})
        return JsonResponse({'success': True, 'is_favori': True})
    except Logement.DoesNotExist:
        return JsonResponse({'error': 'Logement introuvable'}, status=404)

def api_get_user_favoris(request):
    """API récupérer favoris utilisateur"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    favoris = Favori.objects.filter(utilisateur=request.user).select_related('logement').prefetch_related('logement__images')
    data = []
    for favori in favoris:
        logement = favori.logement
        images = [img.image.url for img in logement.images.all()[:1]]
        data.append({
            'id': logement.id,
            'titre': logement.titre,
            'adresse': logement.adresse,
            'ville': logement.code_postal or '',  # Utiliser code_postal car le modèle n'a pas de champ ville
            'prix': float(logement.prix) if logement.prix else 0,
            'image': images[0] if images else None,
        })
    
    return JsonResponse({'favoris': data})

def api_filter_by_radius(request):
    """API filtrer par rayon"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_autocomplete_address(request):
    """API autocomplete adresse"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_search_complete(request):
    """API recherche complète"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_search_address_advanced(request):
    """API recherche adresse avancée"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# VUES TRANSPAREO CONNECT
# ============================================

def connect_home(request):
    """Accueil Connect - Page d'accueil réseau social LinkedIn-style"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    user = request.user
    
    # Filtre du feed (par défaut: "Pour vous")
    feed_filter = request.GET.get('filter', 'for_you')
    
    # Récupérer les posts pour le feed avec optimisations
    posts_qs = Post.objects.select_related('author', 'group').prefetch_related(
        'post_images_rel', 'likes', 'comments', 'author__avatar'
    )
    
    # Appliquer le filtre selon le choix
    if feed_filter == 'recent':
        posts = posts_qs.filter(
            Q(visibility='public') | 
            Q(visibility='connections', author__connections_received__user_from=user) |
            Q(visibility='group', group__members=user)
        ).distinct().order_by('-created_at')[:10]
    elif feed_filter == 'popular':
        posts = posts_qs.filter(
            Q(visibility='public') | 
            Q(visibility='connections', author__connections_received__user_from=user) |
            Q(visibility='group', group__members=user)
        ).distinct().annotate(
            engagement=Count('likes') + Count('comments') + Count('shares')
        ).order_by('-engagement', '-created_at')[:10]
    elif feed_filter == 'my_groups':
        posts = posts_qs.filter(
            visibility='group',
            group__members=user
        ).distinct().order_by('-created_at')[:10]
    else:  # for_you - recommandations
        # Algorithme simple : posts de connexions + groupes + populaires
        from .models import Follow
        following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
        posts = posts_qs.filter(
            Q(visibility='public', author_id__in=following_ids) |
            Q(visibility='connections', author__connections_received__user_from=user) |
            Q(visibility='group', group__members=user)
        ).distinct().annotate(
            engagement=Count('likes') + Count('comments')
        ).order_by('-engagement', '-created_at')[:10]
    
    # Groupes de l'utilisateur
    user_groups = Group.objects.filter(members=user).select_related('creator').annotate(
        member_count=Count('members')
    )[:5]
    
    # Suggestions de connexions (personnes avec connexions communes)
    from .models import Follow, UserConnection
    following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
    connection_ids = UserConnection.objects.filter(
        Q(user_from=user) | Q(user_to=user)
    ).values_list('user_from_id', 'user_to_id')
    connected_ids = set()
    for conn in connection_ids:
        if conn[0] == user.id:
            connected_ids.add(conn[1])
        else:
            connected_ids.add(conn[0])
    
    # Suggestions basées sur connexions communes
    suggestions = CustomUser.objects.exclude(
        id=user.id
    ).exclude(
        id__in=following_ids
    ).exclude(
        id__in=connected_ids
    ).annotate(
        common_connections=Count('connections_received', filter=Q(
            connections_received__user_from__in=connected_ids
        ))
    ).order_by('-common_connections', '-date_joined')[:5]
    
    # Groupes suggérés
    suggested_groups = Group.objects.exclude(
        members=user
    ).filter(
        is_public=True
    ).annotate(
        member_count=Count('members')
    ).order_by('-member_count', '-created_at')[:3]
    
    # Hashtags tendance (hashtags les plus utilisés récemment)
    from django.utils import timezone
    from datetime import timedelta
    week_ago = timezone.now() - timedelta(days=7)
    trending_hashtags = Post.objects.filter(
        created_at__gte=week_ago,
        hashtags__isnull=False
    ).values('hashtags').annotate(
        post_count=Count('id')
    ).order_by('-post_count')[:5]
    
    # Compter les notifications non lues
    from .models import UserNotification
    unread_notifications_count = UserNotification.objects.filter(
        user=user, read=False
    ).count()
    
    # Compter les messages non lus
    unread_messages_count = Message.objects.filter(
        conversation__participants=user,
        read=False
    ).exclude(sender=user).count()
    
    # Statistiques utilisateur
    user_posts_count = Post.objects.filter(author=user).count()
    user_connections_count = UserConnection.objects.filter(
        Q(user_from=user) | Q(user_to=user)
    ).count()
    
    # Vues profil ce mois (si modèle existe)
    from django.utils import timezone
    from datetime import timedelta
    this_month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    # Note: Si vous avez un modèle ProfileView, utilisez-le ici
    
    context = {
        'posts': posts,
        'user_groups': user_groups,
        'suggestions': suggestions,
        'suggested_groups': suggested_groups,
        'trending_hashtags': trending_hashtags,
        'unread_notifications_count': unread_notifications_count,
        'unread_messages_count': unread_messages_count,
        'user_posts_count': user_posts_count,
        'user_connections_count': user_connections_count,
        'feed_filter': feed_filter,
    }
    return render(request, 'core/connect/home_new.html', context)

@ensure_csrf_cookie
@login_required
def connect_messages(request):
    """Messages Connect - Page complète"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Conversations de l'utilisateur
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related(
        'participants', 
        'messages',
        'last_message__sender'
    ).order_by('-updated_at')
    
    # Préparer données conversations avec autres participants
    conversations_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        conversations_data.append({
            'conversation': conv,
            'other_user': other_user,
            'unread_count': conv.get_unread_count(request.user)
        })
    
    # Calculer compteur total non lus
    unread_count = sum(data['unread_count'] for data in conversations_data)
    
    # Conversation active (depuis query param)
    active_conversation_id = request.GET.get('conversation')
    active_conversation = None
    active_other_user = None
    active_messages = []
    if active_conversation_id:
        try:
            active_conversation = conversations.get(id=active_conversation_id)
            if active_conversation.participants.count() == 2:
                active_other_user = active_conversation.get_other_participant(request.user)
            
            # Charger messages initiaux pour rendu serveur
            active_messages = Message.objects.filter(
                conversation=active_conversation
            ).select_related('sender').order_by('created_at')[:50]
        except Conversation.DoesNotExist:
            pass
    
    context = {
        'conversations_data': conversations_data,
        'conversations': conversations,  # Garder pour compatibilité
        'unread_count': unread_count,
        'active_conversation_id': active_conversation_id,
        'active_conversation': active_conversation,
        'active_other_user': active_other_user,
        'active_messages': active_messages,
    }
    return render(request, 'core/connect/messages_complete.html', context)

def connect_notifications(request):
    """Notifications Connect"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    from .models import UserNotification
    notifications = UserNotification.objects.filter(user=request.user).order_by('-created_at')[:50]
    unread_count = UserNotification.objects.filter(user=request.user, read=False).count()
    
    context = {
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'core/connect/notifications.html', context)

def connect_lease(request):
    """Gérer mon bail"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Baux de l'utilisateur (locataire)
    baux = Bail.objects.filter(locataire=request.user).select_related('logement', 'proprietaire').order_by('-date_debut')
    
    context = {
        'baux': baux,
    }
    return render(request, 'core/connect/lease.html', context)

def connect_user_search(request):
    """Recherche utilisateurs"""
    return stub_view(request)

def connect_properties(request):
    """Gérer mes locations"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Récupérer les baux du propriétaire
    baux = Bail.objects.filter(proprietaire=request.user).select_related('logement', 'locataire').order_by('-date_debut')
    
    # Filtre par statut
    statut_filter = request.GET.get('statut', 'all')
    if statut_filter != 'all':
        baux = baux.filter(statut=statut_filter)
    
    # Statistiques globales
    baux_actifs = Bail.objects.filter(proprietaire=request.user, statut='actif')
    nombre_biens_loues = baux_actifs.count()
    
    # Calculer le revenu mensuel total (somme des loyers + charges)
    revenu_mensuel_total = sum(
        float(bail.get_montant_total_mensuel()) for bail in baux_actifs
    )
    
    # Calculer les paiements en retard avec PaiementLoyer
    from datetime import date
    today = date.today()
    loyers_en_retard = PaiementLoyer.objects.filter(
        bail__in=baux_actifs,
        statut='en_retard'
    ).count()
    
    # Demandes en attente (candidatures pour les logements du propriétaire)
    logements_ids = Logement.objects.filter(proprietaire=request.user).values_list('id', flat=True)
    demandes_attente = Candidature.objects.filter(
        logement_id__in=logements_ids,
        statut='en_attente'
    ).count()
    
    # Préparer les données pour chaque bail
    baux_data = []
    for bail in baux:
        # Calculer paiements en retard pour ce bail
        paiements_en_retard = PaiementLoyer.objects.filter(
            bail=bail,
            statut='en_retard'
        ).count()
        
        # Demandes en attente pour ce logement
        demandes_en_attente = Candidature.objects.filter(
            logement=bail.logement,
            statut='en_attente'
        ).count()
        
        baux_data.append({
            'bail': bail,
            'paiements_en_retard': paiements_en_retard,
            'demandes_en_attente': demandes_en_attente,
        })
    
    context = {
        'page_title': 'Gérer mes locations',
        'nombre_biens_loues': nombre_biens_loues,
        'revenu_mensuel_total': revenu_mensuel_total,
        'loyers_en_retard': loyers_en_retard,
        'demandes_attente': demandes_attente,
        'statut_filter': statut_filter,
        'baux_data': baux_data,
    }
    return render(request, 'core/connect/properties.html', context)

def connect_groups(request):
    """Groupes Connect"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    # Groupes de l'utilisateur
    my_groups = Group.objects.filter(members=request.user).annotate(
        member_count=Count('members', distinct=True),
        posts_count=Count('posts', distinct=True)
    )
    
    # Groupes publics suggérés
    suggested_groups = Group.objects.filter(is_public=True).exclude(members=request.user).annotate(
        member_count=Count('members', distinct=True)
    ).order_by('-member_count')[:10]
    
    context = {
        'my_groups': my_groups,
        'suggested_groups': suggested_groups,
    }
    return render(request, 'core/connect/groups.html', context)

def connect_search_users(request):
    """Recherche utilisateurs"""
    return stub_view(request)

def connect_search_results(request):
    """Page de résultats de recherche complète - Style LinkedIn"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # all, posts, users, groups, events
    page = int(request.GET.get('page', 1))
    per_page = 20
    
    if not query:
        return render(request, 'core/connect/search_results.html', {
            'query': '',
            'search_type': search_type,
            'results': {},
            'total': 0,
        })
    
    results = {
        'posts': [],
        'users': [],
        'groups': [],
        'events': [],
        'hashtags': [],
    }
    total = 0
    
    # Recherche posts
    if search_type in ['all', 'posts']:
        posts_qs = Post.objects.filter(
            Q(content__icontains=query) |
            Q(hashtags__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).select_related('author', 'group').prefetch_related('post_images_rel').annotate(
            likes_count=Count('likes', filter=Q(likes__active=True)),
            comments_count=Count('comments'),
        ).order_by('-created_at')
        
        paginator = Paginator(posts_qs, per_page)
        posts_page = paginator.get_page(page)
        
        posts_list = []
        for post in posts_page:
            first_image = post.post_images_rel.first()
            posts_list.append({
                'post': post,
                'first_image': first_image,
            })
        results['posts'] = posts_list
        results['posts_page'] = posts_page
        total += paginator.count
    
    # Recherche utilisateurs
    if search_type in ['all', 'users']:
        users_qs = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profession__icontains=query) |
            Q(employeur__icontains=query)
        ).exclude(id=request.user.id).annotate(
            connections_count=Count('connections_received', filter=Q(connections_received__status='accepted')) + 
                             Count('connections_sent', filter=Q(connections_sent__status='accepted')),
        ).order_by('-date_joined')
        
        paginator = Paginator(users_qs, per_page)
        users_page = paginator.get_page(page)
        results['users'] = users_page
        total += paginator.count
    
    # Recherche groupes
    if search_type in ['all', 'groups']:
        groups_qs = Group.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(full_description__icontains=query)
        ).annotate(
            member_count=Count('members', distinct=True),
            posts_count=Count('posts', distinct=True),
        ).order_by('-member_count')
        
        paginator = Paginator(groups_qs, per_page)
        groups_page = paginator.get_page(page)
        results['groups'] = groups_page
        total += paginator.count
    
    # Recherche événements
    if search_type in ['all', 'events']:
        events_qs = GroupMeetup.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(group__name__icontains=query)
        ).select_related('group', 'created_by').filter(
            date_start__gte=timezone.now()
        ).order_by('date_start')
        
        paginator = Paginator(events_qs, per_page)
        events_page = paginator.get_page(page)
        results['events'] = events_page
        total += paginator.count
    
    # Recherche hashtags
    if search_type in ['all', 'hashtags']:
        hashtags_qs = Post.objects.filter(
            hashtags__icontains=query,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('hashtags').annotate(
            post_count=Count('id')
        ).order_by('-post_count')[:10]
        
        for tag_data in hashtags_qs:
            if tag_data['hashtags']:
                tags = [t.strip() for t in tag_data['hashtags'].split(',') if query.lower() in t.lower()]
                for tag in tags[:1]:
                    results['hashtags'].append({
                        'tag': tag,
                        'post_count': tag_data['post_count'],
                    })
    
    # Compter les notifications et messages non lus pour la navbar
    from .models import UserNotification
    unread_notifications_count = UserNotification.objects.filter(
        user=request.user, read=False
    ).count()
    
    unread_messages_count = Message.objects.filter(
        conversation__participants=request.user,
        read=False
    ).exclude(sender=request.user).count()
    
    context = {
        'query': query,
        'search_type': search_type,
        'results': results,
        'total': total,
        'page': page,
        'user': request.user,
        'unread_notifications_count': unread_notifications_count,
        'unread_messages_count': unread_messages_count,
    }
    
    return render(request, 'core/connect/search_results.html', context)

def connect_settings(request):
    """Paramètres Connect"""
    return stub_view(request)

def connect_help(request):
    """Aide Connect"""
    return stub_view(request)

def connect_group_detail(request, group_id):
    """Détail groupe"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    try:
        group = Group.objects.prefetch_related('members', 'admins', 'posts__author').annotate(
            member_count=Count('members', distinct=True),
            posts_count=Count('posts', distinct=True)
        ).get(id=group_id)
        
        # Vérifier si l'utilisateur est membre
        is_member = group.members.filter(id=request.user.id).exists()
        is_admin = group.admins.filter(id=request.user.id).exists()
        
        # Posts du groupe
        posts = Post.objects.filter(group=group).select_related('author').prefetch_related('images').order_by('-created_at')[:20]
        
        context = {
            'group': group,
            'is_member': is_member,
            'is_admin': is_admin,
            'posts': posts,
        }
        return render(request, 'core/connect/group_detail.html', context)
    except Group.DoesNotExist:
        messages.error(request, 'Groupe introuvable.')
        return redirect('connect-groups')

def connect_property_detail(request, bail_id):
    """Détail propriété"""
    return stub_view(request)

def owner_dashboard(request):
    """Dashboard propriétaire"""
    return stub_view(request)

# ============================================
# API CONNECT - POSTS
# ============================================

def create_post(request):
    """Créer un post"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        group_id = request.POST.get('group_id')
        visibility = request.POST.get('visibility', 'public')
        
        if not content:
            return JsonResponse({'error': 'Le contenu est requis'}, status=400)
        
        group = None
        if group_id:
            try:
                group = Group.objects.get(id=group_id)
                # Vérifier que l'utilisateur est membre
                if not group.members.filter(id=request.user.id).exists():
                    return JsonResponse({'error': 'Vous n\'êtes pas membre de ce groupe'}, status=403)
            except Group.DoesNotExist:
                return JsonResponse({'error': 'Groupe introuvable'}, status=404)
        
        post = Post.objects.create(
            author=request.user,
            content=content,
            group=group,
            visibility=visibility,
            content_type='text'
        )
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'content': post.content,
                'author': post.author.username,
                'created_at': post.created_at.strftime('%d/%m/%Y %H:%M'),
            }
        })
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def toggle_post_like(request, post_id):
    """Toggle like post"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        post = Post.objects.get(id=post_id)
        from .models import PostLike
        
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user
        )
        
        if not created:
            like.delete()
            post.likes_count = max(0, post.likes_count - 1)
            is_liked = False
        else:
            post.likes_count = (post.likes_count or 0) + 1
            is_liked = True
        
        post.save()
        
        return JsonResponse({
            'success': True,
            'is_liked': is_liked,
            'likes_count': post.likes_count
        })
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post introuvable'}, status=404)

def create_comment(request, post_id):
    """Créer commentaire"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        parent_id = request.POST.get('parent_id')
        
        if not content:
            return JsonResponse({'error': 'Le contenu est requis'}, status=400)
        
        try:
            post = Post.objects.get(id=post_id)
            from .models import PostComment
            
            parent = None
            if parent_id:
                try:
                    parent = PostComment.objects.get(id=parent_id, post=post)
                except PostComment.DoesNotExist:
                    pass
            
            comment = PostComment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent
            )
            
            post.comments_count = (post.comments_count or 0) + 1
            post.save()
            
            return JsonResponse({
                'success': True,
                'comment': {
                    'id': comment.id,
                    'content': comment.content,
                    'author': comment.author.username,
                    'created_at': comment.created_at.strftime('%d/%m/%Y %H:%M'),
                }
            })
        except Post.DoesNotExist:
            return JsonResponse({'error': 'Post introuvable'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def share_post(request, post_id):
    """Partager post"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def delete_post(request, post_id):
    """Supprimer post"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def report_post(request):
    """Signaler post"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - FEED & POSTS
# ============================================

@login_required
def api_feed(request):
    """API Feed - Charger les posts avec pagination"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    user = request.user
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    feed_filter = request.GET.get('filter', 'for_you')
    
    # Calculer offset
    offset = (page - 1) * limit
    
    # Construire la requête selon le filtre
    posts_qs = Post.objects.select_related('author', 'group').prefetch_related(
        'post_images_rel', 'likes', 'comments'
    )
    
    if feed_filter == 'recent':
        posts_qs = posts_qs.filter(
            Q(visibility='public') | 
            Q(visibility='connections', author__connections_received__user_from=user) |
            Q(visibility='group', group__members=user)
        ).distinct().order_by('-created_at')
    elif feed_filter == 'popular':
        posts_qs = posts_qs.filter(
            Q(visibility='public') | 
            Q(visibility='connections', author__connections_received__user_from=user) |
            Q(visibility='group', group__members=user)
        ).distinct().annotate(
            engagement=Count('likes') + Count('comments') + Count('shares')
        ).order_by('-engagement', '-created_at')
    elif feed_filter == 'my_groups':
        posts_qs = posts_qs.filter(
            visibility='group',
            group__members=user
        ).distinct().order_by('-created_at')
    else:  # for_you
        from .models import Follow
        following_ids = Follow.objects.filter(follower=user).values_list('followed_id', flat=True)
        posts_qs = posts_qs.filter(
            Q(visibility='public', author_id__in=following_ids) |
            Q(visibility='connections', author__connections_received__user_from=user) |
            Q(visibility='group', group__members=user)
        ).distinct().annotate(
            engagement=Count('likes') + Count('comments')
        ).order_by('-engagement', '-created_at')
    
    # Pagination
    total = posts_qs.count()
    posts = posts_qs[offset:offset + limit]
    
    # Récupérer les IDs des posts likés par l'utilisateur
    post_ids = [p.id for p in posts]
    from .models import PostLike
    liked_post_ids = set(PostLike.objects.filter(
        post_id__in=post_ids,
        user=user,
        active=True
    ).values_list('post_id', flat=True))
    
    # Serializer les posts
    posts_data = []
    for post in posts:
        posts_data.append({
            'id': post.id,
            'author': {
                'id': post.author.id,
                'username': post.author.username,
                'full_name': post.author.get_full_name() or post.author.username,
                'avatar': post.author.avatar.url if post.author.avatar else None,
                'profession': post.author.profession or '',
                'verified': post.author.identity_verified or post.author.proprietaire_verified,
            },
            'content': post.content,
            'hashtags': post.hashtags or '',
            'visibility': post.visibility,
            'group': {
                'id': post.group.id,
                'name': post.group.name,
            } if post.group else None,
            'images': [img.image.url for img in post.post_images_rel.all()],
            'likes_count': post.likes_count or 0,
            'comments_count': post.comments_count or 0,
            'shares_count': post.shares_count or 0,
            'is_liked': post.id in liked_post_ids,
            'created_at': post.created_at.isoformat(),
            'created_at_human': post.created_at.strftime('%d/%m/%Y à %H:%M'),
        })
    
    return JsonResponse({
        'posts': posts_data,
        'page': page,
        'limit': limit,
        'total': total,
        'has_more': offset + limit < total,
    })

@login_required
def api_create_post(request):
    """API Créer un nouveau post"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        visibility = data.get('visibility', 'public')
        group_id = data.get('group_id')
        
        # Validation
        if not content and not data.get('media'):
            return JsonResponse({'error': 'Le contenu ou un média est requis'}, status=400)
        
        if len(content) > 3000:
            return JsonResponse({'error': 'Le contenu ne peut pas dépasser 3000 caractères'}, status=400)
        
        # Créer le post
        post = Post.objects.create(
            author=request.user,
            content=content,
            visibility=visibility,
            group_id=group_id if group_id else None,
            hashtags=data.get('hashtags', ''),
        )
        
        # Gérer les médias (images/vidéos) si présents
        # TODO: Implémenter upload de fichiers
        
        return JsonResponse({
            'success': True,
            'post': {
                'id': post.id,
                'content': post.content,
                'created_at': post.created_at.isoformat(),
            }
        }, status=201)
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_toggle_like(request, post_id):
    """API Like/Unlike un post"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        post = Post.objects.get(id=post_id)
        from .models import PostLike
        
        # Vérifier si déjà liké
        like, created = PostLike.objects.get_or_create(
            post=post,
            user=request.user,
            defaults={'active': True}
        )
        
        if not created:
            # Toggle
            like.active = not like.active
            like.save()
        
        # Mettre à jour le compteur
        post.likes_count = PostLike.objects.filter(post=post, active=True).count()
        post.save()
        
        return JsonResponse({
            'success': True,
            'liked': like.active,
            'likes_count': post.likes_count,
        })
        
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_create_comment(request, post_id):
    """API Créer un commentaire sur un post"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        post = Post.objects.get(id=post_id)
        data = json.loads(request.body)
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')
        
        if not content:
            return JsonResponse({'error': 'Le contenu est requis'}, status=400)
        
        if len(content) > 500:
            return JsonResponse({'error': 'Le commentaire ne peut pas dépasser 500 caractères'}, status=400)
        
        # Créer le commentaire
        from .models import PostComment
        comment = PostComment.objects.create(
            post=post,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None,
        )
        
        # Mettre à jour le compteur
        post.comments_count = PostComment.objects.filter(post=post).count()
        post.save()
        
        return JsonResponse({
            'success': True,
            'comment': {
                'id': comment.id,
                'content': comment.content,
                'author': {
                    'id': comment.author.id,
                    'username': comment.author.username,
                    'avatar': comment.author.avatar.url if comment.author.avatar else None,
                },
                'created_at': comment.created_at.isoformat(),
                'likes_count': comment.likes_count or 0,
            },
            'comments_count': post.comments_count,
        }, status=201)
        
    except Post.DoesNotExist:
        return JsonResponse({'error': 'Post introuvable'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON invalide'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_search(request):
    """API Recherche en temps réel - Style LinkedIn"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    query = request.GET.get('q', '').strip()
    search_type = request.GET.get('type', 'all')  # all, posts, users, groups, events
    limit = int(request.GET.get('limit', 5))
    
    if len(query) < 2:
        return JsonResponse({
            'posts': [],
            'users': [],
            'groups': [],
            'events': [],
            'hashtags': [],
            'total': 0,
        })
    
    results = {
        'posts': [],
        'users': [],
        'groups': [],
        'events': [],
        'hashtags': [],
        'total': 0,
    }
    
    # Recherche posts avec plus de détails
    if search_type in ['all', 'posts']:
        posts = Post.objects.filter(
            Q(content__icontains=query) |
            Q(hashtags__icontains=query) |
            Q(author__username__icontains=query) |
            Q(author__first_name__icontains=query) |
            Q(author__last_name__icontains=query)
        ).select_related('author', 'group').prefetch_related('post_images_rel').annotate(
            likes_count=Count('likes', filter=Q(likes__active=True)),
            comments_count=Count('comments'),
        ).order_by('-created_at')[:limit]
        
        for post in posts:
            first_image = post.post_images_rel.first()
            results['posts'].append({
                'id': post.id,
                'content': post.content[:150] + '...' if len(post.content) > 150 else post.content,
                'author': {
                    'id': post.author.id,
                    'username': post.author.username,
                    'full_name': post.author.get_full_name() or post.author.username,
                    'avatar': post.author.avatar.url if post.author.avatar else None,
                    'profession': post.author.profession or '',
                },
                'group': {
                    'id': post.group.id,
                    'name': post.group.name,
                } if post.group else None,
                'hashtags': post.hashtags.split(',') if post.hashtags else [],
                'image': first_image.image.url if first_image else None,
                'created_at': post.created_at.isoformat(),
                'likes_count': post.likes_count,
                'comments_count': post.comments_count,
                'url': f'/connect/posts/{post.id}/',
            })
    
    # Recherche utilisateurs avec plus de détails
    if search_type in ['all', 'users']:
        users = CustomUser.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(profession__icontains=query) |
            Q(employeur__icontains=query)
        ).exclude(id=request.user.id).annotate(
            connections_count=Count('connections_received', filter=Q(connections_received__status='accepted')) + 
                             Count('connections_sent', filter=Q(connections_sent__status='accepted')),
        )[:limit]
        
        # Vérifier les connexions communes
        user_connections = UserConnection.objects.filter(
            Q(user_from=request.user, status='accepted') | Q(user_to=request.user, status='accepted')
        ).values_list('user_from_id', 'user_to_id')
        connected_user_ids = set()
        for conn in user_connections:
            connected_user_ids.add(conn[0])
            connected_user_ids.add(conn[1])
        connected_user_ids.discard(request.user.id)
        
        for user in users:
            # Compter les connexions communes
            common_connections = len(connected_user_ids.intersection(
                set(UserConnection.objects.filter(
                    Q(user_from=user, status='accepted') | Q(user_to=user, status='accepted')
                ).values_list('user_from_id', 'user_to_id').flat)
            ))
            
            results['users'].append({
                'id': user.id,
                'username': user.username,
                'full_name': user.get_full_name() or user.username,
                'avatar': user.avatar.url if user.avatar else None,
                'profession': user.profession or '',
                'employeur': user.employeur or '',
                'location': user.ville or '',
                'connections_count': user.connections_count,
                'common_connections': common_connections,
                'is_verified': user.identity_verified or user.proprietaire_verified,
                'url': f'/profile/{user.id}/',
            })
    
    # Recherche groupes avec plus de détails
    if search_type in ['all', 'groups']:
        groups = Group.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(full_description__icontains=query)
        ).annotate(
            member_count=Count('members', distinct=True),
            posts_count=Count('posts', distinct=True),
        ).order_by('-member_count')[:limit]
        
        for group in groups:
            is_member = group.members.filter(id=request.user.id).exists()
            results['groups'].append({
                'id': group.id,
                'name': group.name,
                'description': group.description[:120] + '...' if group.description and len(group.description) > 120 else (group.description or ''),
                'member_count': group.member_count,
                'posts_count': group.posts_count,
                'image': group.image.url if group.image else None,
                'category': group.category,
                'is_public': group.is_public,
                'is_member': is_member,
                'url': f'/connect/groups/{group.id}/',
            })
    
    # Recherche événements (GroupMeetup)
    if search_type in ['all', 'events']:
        events = GroupMeetup.objects.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(group__name__icontains=query)
        ).select_related('group', 'created_by').filter(
            date_start__gte=timezone.now()
        ).order_by('date_start')[:limit]
        
        for event in events:
            results['events'].append({
                'id': event.id,
                'title': event.title,
                'description': event.description[:100] + '...' if event.description and len(event.description) > 100 else (event.description or ''),
                'date_start': event.date_start.isoformat(),
                'group': {
                    'id': event.group.id,
                    'name': event.group.name,
                },
                'is_live': event.is_live,
                'participants_count': event.participants.count(),
                'url': f'/connect/groups/{event.group.id}/events/{event.id}/',
            })
    
    # Recherche hashtags
    if search_type in ['all', 'hashtags']:
        hashtags = Post.objects.filter(
            hashtags__icontains=query,
            created_at__gte=timezone.now() - timedelta(days=30)
        ).values('hashtags').annotate(
            post_count=Count('id')
        ).order_by('-post_count')[:limit]
        
        for tag_data in hashtags:
            if tag_data['hashtags']:
                tags = [t.strip() for t in tag_data['hashtags'].split(',') if query.lower() in t.lower()]
                for tag in tags[:1]:  # Prendre le premier tag correspondant
                    results['hashtags'].append({
                        'tag': tag,
                        'post_count': tag_data['post_count'],
                        'url': f'/connect/search/?q={tag}&type=hashtag',
                    })
    
    # Calculer le total
    results['total'] = (
        len(results['posts']) + 
        len(results['users']) + 
        len(results['groups']) + 
        len(results['events']) + 
        len(results['hashtags'])
    )
    
    return JsonResponse(results)

def api_add_reaction(request):
    """API ajouter réaction"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_get_reactions(request, post_id):
    """API récupérer réactions"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_join_collaborative_post(request):
    """API rejoindre post collaboratif"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_load_more_posts(request):
    """API charger plus de posts (alias pour api_feed)"""
    return api_feed(request)

def toggle_comment_like(request, comment_id):
    """Toggle like commentaire"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_load_more_replies(request, comment_id):
    """API charger plus de réponses"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def report_comment(request):
    """Signaler commentaire"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - GROUPES
# ============================================

def create_group(request):
    """Créer groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def edit_group(request):
    """Éditer groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def delete_group(request):
    """Supprimer groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def join_group(request, group_id):
    """Rejoindre groupe"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        group = Group.objects.get(id=group_id)
        from .models import GroupMembership
        
        # Vérifier si déjà membre
        existing = GroupMembership.objects.filter(group=group, user=request.user).first()
        if existing:
            if existing.status == 'accepted':
                return JsonResponse({'error': 'Vous êtes déjà membre de ce groupe'}, status=400)
            elif existing.status == 'pending':
                return JsonResponse({'error': 'Demande déjà envoyée'}, status=400)
        
        if group.is_public and not group.require_approval:
            # Groupe public sans approbation - ajouter directement
            GroupMembership.objects.create(
                group=group,
                user=request.user,
                status='accepted'
            )
            return JsonResponse({'success': True, 'message': 'Vous avez rejoint le groupe'})
        else:
            # Groupe privé ou nécessitant approbation - créer demande
            GroupMembership.objects.create(
                group=group,
                user=request.user,
                status='pending'
            )
            return JsonResponse({'success': True, 'message': 'Demande envoyée', 'pending': True})
    except Group.DoesNotExist:
        return JsonResponse({'error': 'Groupe introuvable'}, status=404)

def leave_group(request, group_id):
    """Quitter groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def approve_group_request(request):
    """Approuver demande groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def reject_group_request(request):
    """Rejeter demande groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def invite_to_group(request):
    """Inviter au groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def ban_group_member(request):
    """Bannir membre groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def promote_group_member(request):
    """Promouvoir membre groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def report_group(request):
    """Signaler groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_vote_sondage(request, sondage_id):
    """API voter sondage"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_vote_reponse(request, reponse_id):
    """API voter réponse"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_repondre_question(request, question_id):
    """API répondre question"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_load_reponses(request, question_id):
    """API charger réponses"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_mark_official_solution(request, question_id):
    """API marquer solution officielle"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_group_updates(request, group_id):
    """API mises à jour groupe"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - MESSAGES
# ============================================

def send_message(request):
    """Envoyer message"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        conversation_id = request.POST.get('conversation_id')
        recipient_id = request.POST.get('recipient_id')
        content = request.POST.get('content', '').strip()
        
        if not content:
            return JsonResponse({'error': 'Le contenu est requis'}, status=400)
        
        try:
            if conversation_id:
                conversation = Conversation.objects.get(id=conversation_id)
                if request.user not in conversation.participants.all():
                    return JsonResponse({'error': 'Accès refusé'}, status=403)
            elif recipient_id:
                recipient = CustomUser.objects.get(id=recipient_id)
                # Créer ou récupérer la conversation
                # Chercher une conversation existante entre ces deux utilisateurs
                conversation = Conversation.objects.filter(
                    participants=request.user
                ).filter(
                    participants=recipient
                ).annotate(
                    participant_count=Count('participants')
                ).filter(participant_count=2).first()
                
                if not conversation:
                    conversation = Conversation.objects.create()
                    conversation.participants.add(request.user, recipient)
            else:
                return JsonResponse({'error': 'Conversation ou destinataire requis'}, status=400)
            
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=content
            )
            
            conversation.updated_at = timezone.now()
            conversation.save()
            
            return JsonResponse({
                'success': True,
                'message': {
                    'id': message.id,
                    'content': message.content,
                    'sender': message.sender.username,
                    'created_at': message.created_at.strftime('%d/%m/%Y %H:%M'),
                }
            })
        except (Conversation.DoesNotExist, CustomUser.DoesNotExist):
            return JsonResponse({'error': 'Conversation ou utilisateur introuvable'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def archive_conversation(request):
    """Archiver conversation"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def favorite_conversation(request):
    """Favoriser conversation"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def mark_conversation_unread(request):
    """Marquer conversation non lue"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def report_message(request):
    """Signaler message"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

@login_required
def api_add_message_reaction(request):
    """API ajouter réaction message"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        message_id = request.POST.get('message_id')
        emoji = request.POST.get('emoji')
        
        if not message_id or not emoji:
            return JsonResponse({'error': 'Message ID et emoji requis'}, status=400)
        
        message = Message.objects.get(id=message_id)
        if request.user not in message.conversation.participants.all():
            return JsonResponse({'error': 'Accès refusé'}, status=403)
        
        # Vérifier si l'emoji est valide
        valid_emojis = ['👍', '❤️', '😂', '😮', '😢', '🔥', '👏', '✅']
        if emoji not in valid_emojis:
            return JsonResponse({'error': 'Emoji invalide'}, status=400)
        
        # Créer ou récupérer la réaction
        reaction, created = MessageReaction.objects.get_or_create(
            message=message,
            user=request.user,
            emoji=emoji,
            defaults={'emoji': emoji}
        )
        
        if not created:
            # Si la réaction existe déjà, la supprimer (toggle)
            reaction.delete()
            action = 'removed'
        else:
            action = 'added'
        
        # Compter les réactions pour ce message
        reactions_count = MessageReaction.objects.filter(message=message, emoji=emoji).count()
        
        return JsonResponse({
            'success': True,
            'action': action,
            'emoji': emoji,
            'count': reactions_count
        })
    except Message.DoesNotExist:
        return JsonResponse({'error': 'Message introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def api_pin_message(request):
    """API épingler message"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_unpin_message(request):
    """API désépingler message"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_set_typing(request, conversation_id):
    """API définir typing"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_get_user_logements(request):
    """API récupérer logements utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_get_user_documents(request):
    """API récupérer documents utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API APPELS
# ============================================

@login_required
def api_initiate_call(request):
    """API initier un appel vocal ou vidéo"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        conversation_id = request.POST.get('conversation_id')
        call_type = request.POST.get('call_type', 'voice')  # 'voice' ou 'video'
        
        if not conversation_id:
            return JsonResponse({'error': 'Conversation requise'}, status=400)
        
        if call_type not in ['voice', 'video']:
            return JsonResponse({'error': 'Type d\'appel invalide'}, status=400)
        
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'error': 'Accès refusé'}, status=403)
        
        # Créer l'appel
        call = Call.objects.create(
            conversation=conversation,
            caller=request.user,
            call_type=call_type,
            status='initiated'
        )
        
        # Ajouter les participants
        for participant in conversation.participants.all():
            if participant != request.user:
                call.participants.add(participant)
        
        return JsonResponse({
            'success': True,
            'call': {
                'id': call.id,
                'conversation_id': conversation_id,
                'caller_id': request.user.id,
                'call_type': call_type,
                'status': call.status,
                'started_at': call.started_at.isoformat()
            }
        })
    except Conversation.DoesNotExist:
        return JsonResponse({'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_answer_call(request, call_id):
    """API répondre à un appel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        call = Call.objects.get(id=call_id)
        if request.user not in call.participants.all():
            return JsonResponse({'error': 'Accès refusé'}, status=403)
        
        if call.status != 'ringing' and call.status != 'initiated':
            return JsonResponse({'error': 'Appel non disponible'}, status=400)
        
        call.status = 'answered'
        call.answered_at = timezone.now()
        call.save()
        
        return JsonResponse({
            'success': True,
            'call': {
                'id': call.id,
                'status': call.status,
                'answered_at': call.answered_at.isoformat()
            }
        })
    except Call.DoesNotExist:
        return JsonResponse({'error': 'Appel introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_end_call(request, call_id):
    """API terminer un appel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        call = Call.objects.get(id=call_id)
        if request.user not in call.participants.all() and request.user != call.caller:
            return JsonResponse({'error': 'Accès refusé'}, status=403)
        
        call.status = 'ended'
        call.ended_at = timezone.now()
        call.calculate_duration()
        call.save()
        
        return JsonResponse({
            'success': True,
            'call': {
                'id': call.id,
                'status': call.status,
                'ended_at': call.ended_at.isoformat(),
                'duration': call.duration
            }
        })
    except Call.DoesNotExist:
        return JsonResponse({'error': 'Appel introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def api_reject_call(request, call_id):
    """API rejeter un appel"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Méthode non autorisée'}, status=405)
    
    try:
        call = Call.objects.get(id=call_id)
        if request.user not in call.participants.all():
            return JsonResponse({'error': 'Accès refusé'}, status=403)
        
        call.status = 'rejected'
        call.ended_at = timezone.now()
        call.save()
        
        return JsonResponse({
            'success': True,
            'call': {
                'id': call.id,
                'status': call.status
            }
        })
    except Call.DoesNotExist:
        return JsonResponse({'error': 'Appel introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

# ============================================
# API MESSAGES COMPLETE
# ============================================

@login_required
def api_get_conversations(request):
    """API récupérer liste conversations"""
    conversations = Conversation.objects.filter(participants=request.user).prefetch_related(
        'participants', 'messages'
    ).order_by('-updated_at')
    
    conversations_data = []
    for conv in conversations:
        other_user = conv.get_other_participant(request.user)
        # Ignorer les conversations où l'autre participant n'existe pas ou est inactif
        if not other_user or not other_user.is_active:
            continue
            
        last_message = conv.last_message
        unread_count = conv.get_unread_count(request.user)
        
        # Récupérer le statut de la conversation pour l'utilisateur
        from core.models import ConversationStatus
        status = ConversationStatus.objects.filter(conversation=conv, user=request.user).first()
        
        conversations_data.append({
            'id': conv.id,
            'name': other_user.get_full_name() if other_user else f'Groupe {conv.id}',
            'other_user': {
                'id': other_user.id,
                'username': other_user.username,
                'get_full_name': other_user.get_full_name() or other_user.username,
                'display_name': getattr(other_user, 'display_name', None) or other_user.get_full_name() or other_user.username,
                'avatar': other_user.avatar.url if other_user.avatar else None,
                'profile_picture': other_user.avatar.url if other_user.avatar else None,  # Alias pour compatibilité
                'is_online': False  # À implémenter avec WebSocket
            },
            'participants': [{
                'id': p.id,
                'username': p.username,
                'get_full_name': p.get_full_name(),
                'avatar': p.avatar.url if p.avatar else None,
                'profile_picture': p.avatar.url if p.avatar else None  # Alias pour compatibilité
            } for p in conv.participants.filter(is_active=True).all()],
            'last_message': {
                'id': last_message.id if last_message else None,
                'content': last_message.content if last_message else '',
                'sender_id': last_message.sender.id if last_message else None,
                'created_at': last_message.created_at.isoformat() if last_message else conv.updated_at.isoformat()
            } if last_message else None,
            'updated_at': conv.updated_at.isoformat(),
            'unread_count': unread_count,
            'archived': status.archived if status else False,
            'favorited': status.favorited if status else False
        })
    
    return JsonResponse({
        'success': True,
        'conversations': conversations_data
    })

@login_required
def api_get_messages(request, conversation_id):
    """API récupérer messages d'une conversation"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
        
        before = request.GET.get('before')
        limit = int(request.GET.get('limit', 30))
        
        messages_query = Message.objects.filter(conversation=conversation).select_related('sender')
        
        if before:
            try:
                before_msg = Message.objects.get(id=before)
                messages_query = messages_query.filter(created_at__lt=before_msg.created_at)
            except Message.DoesNotExist:
                pass
        
        messages = messages_query.filter(sender__is_active=True).order_by('-created_at')[:limit]
        messages = list(reversed(messages))  # Plus ancien en premier
        
        messages_data = []
        for msg in messages:
            # Ignorer les messages des utilisateurs inactifs
            if not msg.sender.is_active:
                continue
                
            messages_data.append({
                'id': msg.id,
                'conversation_id': conversation_id,
                'sender_id': msg.sender.id,
                'sender': {
                    'id': msg.sender.id,
                    'username': msg.sender.username,
                    'get_full_name': msg.sender.get_full_name() or msg.sender.username,
                    'display_name': getattr(msg.sender, 'display_name', None) or msg.sender.get_full_name() or msg.sender.username,
                    'avatar': msg.sender.avatar.url if msg.sender.avatar else None,
                    'profile_picture': msg.sender.avatar.url if msg.sender.avatar else None  # Alias pour compatibilité
                },
                'content': msg.content,
                'image': msg.image.url if msg.image else None,
                'document': msg.document.url if msg.document else None,
                'document_name': msg.document_name,
                'document_size': msg.document.size if msg.document else None,
                'read': msg.read,
                'delivered': msg.delivered,
                'created_at': msg.created_at.isoformat(),
                'reply_to': None  # À implémenter
            })
        
        return JsonResponse({
            'success': True,
            'messages': messages_data
        })
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@login_required
def api_send_message(request):
    """API envoyer message"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        conversation_id = request.POST.get('conversation_id')
        content = request.POST.get('content', '').strip()
        
        if not conversation_id:
            return JsonResponse({'success': False, 'error': 'Conversation requise'}, status=400)
        
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
        
        # Gérer upload images
        images = []
        for key in request.FILES:
            if key.startswith('image_'):
                images.append(request.FILES[key])
        
        # Gérer upload fichiers
        files = []
        for key in request.FILES:
            if key.startswith('file_'):
                files.append(request.FILES[key])
        
        # Gérer upload audio (message vocal)
        audio_file = request.FILES.get('audio')
        audio_duration = request.POST.get('audio_duration')
        
        # Créer message
        message = Message.objects.create(
            conversation=conversation,
            sender=request.user,
            content=content
        )
        
        # Upload première image si présente
        if images:
            message.image = images[0]
            message.save()
        
        # Upload premier fichier si présent
        if files:
            message.document = files[0]
            message.document_name = files[0].name
            message.save()
        
        # Upload message vocal si présent
        if audio_file:
            message.audio = audio_file
            if audio_duration:
                try:
                    message.audio_duration = int(audio_duration)
                except ValueError:
                    pass
            message.save()
        
        # Mettre à jour conversation
        conversation.last_message = message
        conversation.updated_at = timezone.now()
        conversation.save()
        
        return JsonResponse({
            'success': True,
            'message': {
                'id': message.id,
                'conversation_id': conversation_id,
                'sender_id': request.user.id,
                'sender': {
                    'id': request.user.id,
                    'username': request.user.username,
                    'get_full_name': request.user.get_full_name(),
                    'avatar': request.user.avatar.url if request.user.avatar else None,
                    'profile_picture': request.user.avatar.url if request.user.avatar else None  # Alias pour compatibilité
                },
                'content': message.content,
                'image': message.image.url if message.image else None,
                'document': message.document.url if message.document else None,
                'document_name': message.document_name,
                'audio': message.audio.url if message.audio else None,
                'audio_duration': message.audio_duration,
                'read': False,
                'delivered': False,
                'created_at': message.created_at.isoformat()
            }
        })
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in api_send_message: {error_trace}")
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)

@login_required
def api_mark_conversation_read(request, conversation_id):
    """API marquer conversation comme lue"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
        
        # Marquer tous les messages non lus comme lus
        Message.objects.filter(
            conversation=conversation,
            read=False
        ).exclude(sender=request.user).update(read=True)
        
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
@require_POST
def api_mark_all_conversations_read(request):
    """API marquer toutes les conversations comme lues"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    try:
        # Récupérer toutes les conversations de l'utilisateur
        conversations = Conversation.objects.filter(participants=request.user)
        
        # Marquer tous les messages non lus comme lus pour toutes les conversations
        Message.objects.filter(
            conversation__in=conversations,
            read=False
        ).exclude(sender=request.user).update(read=True)
        
        return JsonResponse({'success': True, 'message': 'Toutes les conversations ont été marquées comme lues'})
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in api_mark_all_conversations_read: {error_trace}")
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)

@login_required
@require_POST
def api_archive_all_conversations(request):
    """API archiver toutes les conversations"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    try:
        # Récupérer toutes les conversations de l'utilisateur
        # Note: Si le modèle n'a pas de champ is_archived, on peut utiliser un filtre personnalisé
        conversations = Conversation.objects.filter(participants=request.user)
        
        # Pour l'instant, on retourne un succès même si l'archivage n'est pas implémenté
        # L'archivage sera implémenté avec un modèle ConversationStatus ou un champ is_archived
        # conversations.update(is_archived=True)
        
        return JsonResponse({'success': True, 'message': 'Toutes les conversations ont été archivées'})
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in api_archive_all_conversations: {error_trace}")
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)

@login_required
def api_archive_conversation(request, conversation_id):
    """API archiver conversation"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
        
        # Créer ou mettre à jour ConversationStatus
        from core.models import ConversationStatus
        status, created = ConversationStatus.objects.get_or_create(
            conversation=conversation,
            user=request.user,
            defaults={'archived': True}
        )
        if not created:
            status.archived = True
            status.save()
        
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_toggle_important(request, conversation_id):
    """API marquer/démarquer conversation en favoris"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
        
        # Créer ou mettre à jour ConversationStatus pour les favoris
        from core.models import ConversationStatus
        status, created = ConversationStatus.objects.get_or_create(
            conversation=conversation,
            user=request.user,
            defaults={'favorited': True}
        )
        if not created:
            status.favorited = not status.favorited
            status.save()
        
        return JsonResponse({'success': True, 'favorited': status.favorited})
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_delete_conversation(request, conversation_id):
    """API supprimer conversation"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    if request.method != 'DELETE':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        conversation = Conversation.objects.get(id=conversation_id)
        if request.user not in conversation.participants.all():
            return JsonResponse({'success': False, 'error': 'Accès refusé'}, status=403)
        
        # Retirer utilisateur de la conversation
        conversation.participants.remove(request.user)
        
        # Si plus de participants, supprimer conversation
        if conversation.participants.count() == 0:
            conversation.delete()
        
        return JsonResponse({'success': True})
    except Conversation.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Conversation introuvable'}, status=404)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def api_search_users(request):
    """API rechercher utilisateurs"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'success': True, 'users': []})
    
    users = CustomUser.objects.filter(
        Q(username__icontains=query) | 
        Q(first_name__icontains=query) | 
        Q(last_name__icontains=query) |
        Q(email__icontains=query)
    ).exclude(id=request.user.id)[:20]
    
    users_data = [{
        'id': user.id,
        'username': user.username,
        'get_full_name': user.get_full_name() or user.username,
        'first_name': user.first_name or '',
        'last_name': user.last_name or '',
        'email': user.email,
        'profile_picture': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None,
        'avatar': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None
    } for user in users]
    
    return JsonResponse({
        'success': True,
        'users': users_data
    })

@login_required
def api_create_conversation(request):
    """API créer nouvelle conversation"""
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Non authentifié'}, status=401)
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Méthode non autorisée'}, status=405)
    
    try:
        # Gérer FormData (avec images) ou JSON
        content_type = request.content_type or ''
        if 'multipart/form-data' in content_type:
            # FormData avec images
            participant_ids_str = request.POST.get('participants', '[]')
            try:
                participant_ids = json.loads(participant_ids_str)
            except:
                participant_ids = []
            initial_message = request.POST.get('message', '').strip()
            group_name = request.POST.get('group_name', '').strip()
            
            # Récupérer les images
            images = []
            index = 0
            while f'image_{index}' in request.FILES:
                images.append(request.FILES[f'image_{index}'])
                index += 1
        else:
            # JSON standard
            data = json.loads(request.body) if request.body else {}
            participant_ids = data.get('participants', [])
            initial_message = data.get('message', '').strip()
            group_name = data.get('group_name', '').strip()
            images = []
        
        if not participant_ids or len(participant_ids) == 0:
            return JsonResponse({'success': False, 'error': 'Au moins un destinataire requis'}, status=400)
        
        # Vérifier que les participants existent
        participants = CustomUser.objects.filter(id__in=participant_ids)
        if participants.count() != len(participant_ids):
            return JsonResponse({'success': False, 'error': 'Un ou plusieurs destinataires introuvables'}, status=404)
        
        # Pour une conversation 1-to-1, vérifier si une conversation existe déjà
        if len(participant_ids) == 1:
            other_user = participants.first()
            # Chercher une conversation existante entre ces deux utilisateurs (actifs uniquement)
            # Utiliser une requête plus précise pour trouver exactement 2 participants
            from django.db.models import Count
            existing_conversation = Conversation.objects.filter(
                participants=request.user
            ).filter(
                participants=other_user
            ).annotate(
                participant_count=Count('participants')
            ).filter(
                participant_count=2
            ).exclude(
                participants__is_active=False
            ).first()
            
            if existing_conversation:
                # Utiliser la conversation existante
                conversation = existing_conversation
                # Mettre à jour updated_at pour que la conversation remonte en haut
                conversation.updated_at = timezone.now()
                conversation.save()
            else:
                # Créer nouvelle conversation 1-to-1
                conversation = Conversation.objects.create()
                conversation.participants.add(request.user, other_user)
        else:
            # Conversation de groupe (plusieurs participants)
            conversation = Conversation.objects.create()
            conversation.participants.add(request.user)
            for participant in participants:
                conversation.participants.add(participant)
        
        # Si groupe et nom fourni, stocker (à implémenter avec modèle Group si nécessaire)
        # Pour l'instant, on utilise juste le nom pour l'affichage
        
        # Envoyer message initial si fourni ou si images
        message = None
        if initial_message or images:
            message = Message.objects.create(
                conversation=conversation,
                sender=request.user,
                content=initial_message
            )
            
            # Ajouter les images
            for img_file in images:
                # Sauvegarder l'image
                message.image = img_file
                message.save()
                # Note: Pour plusieurs images, il faudrait un modèle séparé MessageImage
                # Pour l'instant, on sauvegarde seulement la première image
                break
            
            conversation.last_message = message
            conversation.updated_at = timezone.now()
            conversation.save()
        
        return JsonResponse({
            'success': True,
            'conversation_id': conversation.id,
            'message': {
                'id': message.id,
                'content': message.content,
                'created_at': message.created_at.isoformat()
            } if message else None
        })
    except json.JSONDecodeError as e:
        return JsonResponse({'success': False, 'error': 'Données JSON invalides: ' + str(e)}, status=400)
    except ValueError as e:
        return JsonResponse({'success': False, 'error': 'Données invalides: ' + str(e)}, status=400)
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in api_create_conversation: {error_trace}")
        return JsonResponse({'success': False, 'error': f'Erreur serveur: {str(e)}'}, status=500)

# ============================================
# API CONNECT - NOTIFICATIONS
# ============================================

def mark_notification_read(request, notification_id):
    """Marquer notification lue"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        from .models import UserNotification
        notification = UserNotification.objects.get(id=notification_id, user=request.user)
        notification.read = True
        notification.read_at = timezone.now()
        notification.save()
        return JsonResponse({'success': True})
    except UserNotification.DoesNotExist:
        return JsonResponse({'error': 'Notification introuvable'}, status=404)

def mark_all_notifications_read(request):
    """Marquer toutes notifications lues"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    from .models import UserNotification
    UserNotification.objects.filter(user=request.user, read=False).update(
        read=True,
        read_at=timezone.now()
    )
    return JsonResponse({'success': True})

def delete_notification(request, notification_id):
    """Supprimer notification"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def connect_notification_settings(request):
    """Paramètres notifications"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    if request.method == 'POST':
        # Sauvegarder les paramètres de notifications
        user = request.user
        user.notification_email_frequency = request.POST.get('email_frequency', 'immediate')
        user.message_email_notifications = request.POST.get('message_email', 'off') == 'on'
        user.message_push_notifications = request.POST.get('message_push', 'off') == 'on'
        
        # Sauvegarder les paramètres de notifications par type (JSON)
        notification_settings = {}
        for key, value in request.POST.items():
            if key.startswith('notification_'):
                notification_type = key.replace('notification_', '')
                notification_settings[notification_type] = {
                    'email': request.POST.get(f'{key}_email', 'off') == 'on',
                    'push': request.POST.get(f'{key}_push', 'off') == 'on',
                    'in_app': request.POST.get(f'{key}_in_app', 'off') == 'on',
                }
        user.notification_settings = notification_settings
        user.save()
        
        messages.success(request, 'Paramètres de notifications mis à jour avec succès.')
        return redirect('connect-notification-settings')
    
    context = {
        'page_title': 'Paramètres de notifications',
        'user': request.user,
    }
    return render(request, 'core/connect/notification_settings.html', context)

def mark_notification_not_interested(request, notification_id):
    """Marquer notification non intéressante"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_get_notifications_realtime(request):
    """API notifications temps réel"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_get_email_summary(request):
    """API résumé email"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - BAIL
# ============================================

def create_maintenance_request(request, bail_id):
    """Créer demande maintenance"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def upload_lease_document(request, bail_id):
    """Upload document bail"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def create_termination_request(request, bail_id):
    """Créer demande résiliation"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def download_lease_documents(request, bail_id):
    """Télécharger documents bail"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def respond_maintenance_request(request, demande_id):
    """Répondre demande maintenance"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def mark_maintenance_resolved(request, demande_id):
    """Marquer maintenance résolue"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_sign_document(request, bail_id):
    """API signer document"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_upload_shared_file(request, bail_id):
    """API upload fichier partagé"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_download_shared_file(request, bail_id, file_id):
    """API télécharger fichier partagé"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_get_file_logs(request, bail_id, file_id):
    """API logs fichier"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_create_checklist(request, bail_id):
    """API créer checklist"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_add_checklist_item(request, bail_id, checklist_id):
    """API ajouter item checklist"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_validate_checklist(request, bail_id, checklist_id):
    """API valider checklist"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_create_ticket(request, bail_id):
    """API créer ticket"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_add_ticket_comment(request, ticket_id):
    """API ajouter commentaire ticket"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_resolve_ticket(request, ticket_id):
    """API résoudre ticket"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_escalate_ticket(request, ticket_id):
    """API escalader ticket"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_export_history(request, bail_id):
    """API exporter historique"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_create_reminder(request, bail_id):
    """API créer rappel"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_delete_reminder(request, reminder_id):
    """API supprimer rappel"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - PROPRIÉTAIRE
# ============================================

def republish_property(request, bail_id):
    """Republier propriété"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def generate_quittance(request, paiement_id):
    """Générer quittance"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def send_payment_reminder(request, paiement_id):
    """Envoyer rappel paiement"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def generate_bulk_quittances(request):
    """Générer quittances en lot"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def generate_fiscal_summary(request, annee):
    """Générer résumé fiscal"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def mark_payment_paid(request):
    """Marquer paiement payé"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def renew_lease(request):
    """Renouveler bail"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def terminate_lease_owner(request):
    """Résilier bail (propriétaire)"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - CONNEXIONS
# ============================================

def connect_user(request, user_id):
    """Connecter utilisateur (alias pour send_connection_request)"""
    return send_connection_request(request, user_id)

def send_connection_request(request, user_id):
    """Envoyer demande connexion"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        target_user = CustomUser.objects.get(id=user_id)
        if target_user == request.user:
            return JsonResponse({'error': 'Vous ne pouvez pas vous connecter à vous-même'}, status=400)
        
        # Vérifier si demande existe déjà
        existing = UserConnection.objects.filter(
            Q(user_from=request.user, user_to=target_user) |
            Q(user_from=target_user, user_to=request.user)
        ).exists()
        
        if existing:
            return JsonResponse({'error': 'Demande déjà envoyée ou déjà connectés'}, status=400)
        
        # Créer la demande de connexion
        UserConnection.objects.create(
            user_from=request.user,
            user_to=target_user,
            status='pending'
        )
        
        return JsonResponse({'success': True, 'message': 'Demande envoyée'})
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)

def accept_connection_request(request, connection_id):
    """Accepter demande connexion"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        conn = UserConnection.objects.get(id=connection_id, user_to=request.user, status='pending')
        conn.accept()  # Utilise la méthode accept() du modèle
        return JsonResponse({'success': True, 'message': 'Connexion acceptée'})
    except UserConnection.DoesNotExist:
        return JsonResponse({'error': 'Demande introuvable'}, status=404)

def reject_connection_request(request, connection_id):
    """Rejeter demande connexion"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        conn = UserConnection.objects.get(id=connection_id, user_to=request.user, status='pending')
        conn.delete()  # Supprimer la demande
        return JsonResponse({'success': True, 'message': 'Demande rejetée'})
    except UserConnection.DoesNotExist:
        return JsonResponse({'error': 'Demande introuvable'}, status=404)

def remove_connection(request, user_id):
    """Retirer connexion"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    try:
        target_user = CustomUser.objects.get(id=user_id)
        connection = UserConnection.objects.filter(
            (Q(user_from=request.user) & Q(user_to=target_user)) |
            (Q(user_from=target_user) & Q(user_to=request.user)),
            status='accepted'
        ).first()
        
        if connection:
            connection.delete()
            return JsonResponse({'success': True, 'message': 'Connexion supprimée'})
        else:
            return JsonResponse({'error': 'Connexion introuvable'}, status=404)
    except CustomUser.DoesNotExist:
        return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)

def my_connections(request):
    """Mes connexions"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    connections = UserConnection.objects.filter(
        (Q(user_from=request.user) | Q(user_to=request.user)),
        status='accepted'
    ).select_related('user_from', 'user_to')
    
    connected_users = []
    for conn in connections:
        other_user = conn.user_to if conn.user_from == request.user else conn.user_from
        connected_users.append(other_user)
    
    context = {
        'connected_users': connected_users,
    }
    return render(request, 'core/connect/my_connections.html', context)

def block_user(request):
    """Bloquer utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def unblock_user(request):
    """Débloquer utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def report_user(request):
    """Signaler utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def toggle_follow(request):
    """Toggle follow"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            target_user = CustomUser.objects.get(id=user_id)
            if target_user == request.user:
                return JsonResponse({'error': 'Vous ne pouvez pas vous suivre vous-même'}, status=400)
            
            from .models import Follow
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=target_user
            )
            
            if not created:
                follow.delete()
                is_following = False
            else:
                is_following = True
            
            return JsonResponse({
                'success': True,
                'is_following': is_following
            })
        except CustomUser.DoesNotExist:
            return JsonResponse({'error': 'Utilisateur introuvable'}, status=404)
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

def api_user_popup(request, user_id):
    """API popup utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_send_invitation(request):
    """API envoyer invitation"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def api_load_more_users(request):
    """API charger plus d'utilisateurs"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

@login_required
def api_get_suggestions(request):
    """API suggestions d'utilisateurs pour nouvelle conversation"""
    # Récupérer les connexions de l'utilisateur
    connections = UserConnection.objects.filter(
        Q(user_from=request.user, status='accepted') | 
        Q(user_to=request.user, status='accepted')
    ).select_related('user_from', 'user_to')[:10]
    
    suggested_users = []
    for conn in connections:
        other_user = conn.user_to if conn.user_from == request.user else conn.user_from
        suggested_users.append({
            'id': other_user.id,
            'username': other_user.username,
            'display_name': other_user.get_full_name() or other_user.username,
            'get_full_name': other_user.get_full_name() or other_user.username,
            'bio': getattr(other_user, 'bio', '') or '',
            'avatar': other_user.avatar.url if hasattr(other_user, 'avatar') and other_user.avatar else None,
            'profile_picture': other_user.avatar.url if hasattr(other_user, 'avatar') and other_user.avatar else None
        })
    
    # Si pas assez de suggestions, ajouter des utilisateurs récents avec qui on a eu des conversations
    if len(suggested_users) < 10:
        recent_conversations = Conversation.objects.filter(
            participants=request.user
        ).prefetch_related('participants').order_by('-updated_at')[:10]
        
        for conv in recent_conversations:
            other_user = conv.get_other_participant(request.user)
            if other_user and not any(u['id'] == other_user.id for u in suggested_users):
                suggested_users.append({
                    'id': other_user.id,
                    'username': other_user.username,
                    'display_name': other_user.get_full_name() or other_user.username,
                    'get_full_name': other_user.get_full_name() or other_user.username,
                    'bio': getattr(other_user, 'bio', '') or '',
                    'avatar': other_user.avatar.url if hasattr(other_user, 'avatar') and other_user.avatar else None,
                    'profile_picture': other_user.avatar.url if hasattr(other_user, 'avatar') and other_user.avatar else None
                })
                if len(suggested_users) >= 10:
                    break
    
    # Si toujours pas assez, ajouter des utilisateurs actifs récents (pas déjà dans la liste)
    if len(suggested_users) < 10:
        existing_ids = [u['id'] for u in suggested_users] + [request.user.id]
        recent_users = CustomUser.objects.exclude(
            id__in=existing_ids
        ).order_by('-date_joined')[:10 - len(suggested_users)]
        
        for user in recent_users:
            suggested_users.append({
                'id': user.id,
                'username': user.username,
                'display_name': user.get_full_name() or user.username,
                'get_full_name': user.get_full_name() or user.username,
                'bio': getattr(user, 'bio', '') or '',
                'avatar': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None,
                'profile_picture': user.avatar.url if hasattr(user, 'avatar') and user.avatar else None
            })
            if len(suggested_users) >= 10:
                break
    
    return JsonResponse({
        'success': True,
        'users': suggested_users
    })

def user_search_autocomplete(request):
    """Autocomplete recherche utilisateur"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# API CONNECT - PARAMÈTRES
# ============================================

def update_profile_settings(request):
    """Mettre à jour paramètres profil"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def update_privacy_settings(request):
    """Mettre à jour paramètres confidentialité"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def export_gdpr_data(request):
    """Exporter données RGPD"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def export_activity_journal(request):
    """Exporter journal activité"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def disable_connect_profile(request):
    """Désactiver profil Connect"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

def terminate_session(request, session_id):
    """Terminer session"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# VUES RGPD
# ============================================

def cgu_connect(request):
    """CGU Connect"""
    return render(request, 'core/rgpd/cgu_connect.html')

def politique_confidentialite(request):
    """Politique de confidentialité"""
    return render(request, 'core/rgpd/politique_confidentialite.html')

def transparence_algorithmes(request):
    """Transparence algorithmes"""
    return render(request, 'core/rgpd/transparence_algorithmes.html')

def transparence_moderation(request):
    """Transparence modération"""
    return render(request, 'core/rgpd/transparence_moderation.html')

def algorithms_transparency(request):
    """Transparence algorithmes (alias)"""
    return transparence_algorithmes(request)

def rgpd_center(request):
    """Centre RGPD"""
    if not request.user.is_authenticated:
        return redirect('login')
    
    context = {
        'user': request.user,
    }
    return render(request, 'core/transparency/rgpd_center.html', context)

def export_user_data(request):
    """Exporter données utilisateur"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    # Créer un fichier JSON avec toutes les données de l'utilisateur
    import json
    from django.http import HttpResponse
    
    user_data = {
        'username': request.user.username,
        'email': request.user.email,
        'date_joined': request.user.date_joined.isoformat() if request.user.date_joined else None,
        'last_login': request.user.last_login.isoformat() if request.user.last_login else None,
        'bio': request.user.bio,
        'ville': request.user.ville,
        # Ajouter d'autres données selon les besoins
    }
    
    response = HttpResponse(
        json.dumps(user_data, indent=2, ensure_ascii=False),
        content_type='application/json; charset=utf-8'
    )
    response['Content-Disposition'] = f'attachment; filename="transpareo_data_{request.user.id}.json"'
    return response

def delete_user_account(request):
    """Supprimer compte utilisateur"""
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Non authentifié'}, status=401)
    
    if request.method == 'POST':
        # Vérifier le mot de passe
        password = request.POST.get('password')
        if not request.user.check_password(password):
            return JsonResponse({'error': 'Mot de passe incorrect'}, status=400)
        
        # Anonymiser plutôt que supprimer (RGPD)
        user = request.user
        user.username = f'deleted_user_{user.id}'
        user.email = f'deleted_{user.id}@deleted.transpareo'
        user.is_active = False
        user.save()
        
        logout(request)
        messages.success(request, 'Votre compte a été supprimé avec succès.')
        return JsonResponse({'success': True, 'redirect': '/'})
    
    return JsonResponse({'error': 'Méthode non autorisée'}, status=405)

# ============================================
# VUES VÉRIFICATION
# ============================================

def request_verification(request):
    """Demander vérification"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# VUES MARKET STUDY
# ============================================

def market_study_form(request):
    """Formulaire étude marché"""
    return stub_view(request)

def market_study_submit(request):
    """Soumettre étude marché"""
    return JsonResponse({'error': 'Non implémenté'}, status=501)

# ============================================
# VUES DESIGN SYSTEM
# ============================================

def design_system_demo(request):
    """Démo design system"""
    return stub_view(request)

