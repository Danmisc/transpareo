"""
Utilitaires d'authentification avancée
2FA, Magic Link, Badges, etc.
"""
import pyotp
import qrcode
import io
import base64
import secrets
import string
from django.utils import timezone
from datetime import timedelta, date
from django.conf import settings
from django.core.mail import send_mail
from .models import (
    CustomUser, MagicLinkToken, TwoFactorBackupCode, 
    Badge, UserBadge, UserNotification, SecurityAlert,
    Bail, PaiementLoyer
)


def generate_2fa_secret():
    """Génère un secret pour 2FA"""
    return pyotp.random_base32()


def generate_2fa_qr_code(user, secret):
    """Génère un QR code pour l'authentification 2FA"""
    totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
        name=user.email,
        issuer_name="Transpareo"
    )
    
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(totp_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    
    # Convertir en base64 pour l'affichage dans le template
    img_str = base64.b64encode(buffer.read()).decode()
    return f"data:image/png;base64,{img_str}"


def verify_2fa_code(user, code):
    """Vérifie un code 2FA"""
    if not user.two_factor_enabled or not user.two_factor_secret:
        return False
    
    totp = pyotp.TOTP(user.two_factor_secret)
    return totp.verify(code, valid_window=1)


def generate_backup_codes(user, count=10):
    """Génère des codes de secours pour 2FA"""
    codes = []
    for _ in range(count):
        code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        codes.append(code)
        TwoFactorBackupCode.objects.create(user=user, code=code)
    return codes


def create_magic_link(user, ip_address=None):
    """Crée un magic link pour l'authentification"""
    token = secrets.token_urlsafe(32)
    expires_at = timezone.now() + timedelta(minutes=15)
    
    MagicLinkToken.objects.create(
        user=user,
        token=token,
        expires_at=expires_at,
        ip_address=ip_address,
        used=False
    )
    
    return token


def send_magic_link_email(user, token):
    """Envoie un email avec un magic link"""
    magic_link_url = f"{settings.SITE_URL}/auth/magic-link/{token}/"
    
    subject = "Connexion à Transpareo"
    message = f"""
    Bonjour {user.first_name or user.username},
    
    Vous avez demandé à vous connecter à Transpareo.
    Cliquez sur le lien suivant pour vous connecter (lien valide 15 minutes) :
    
    {magic_link_url}
    
    Si vous n'avez pas demandé cette connexion, ignorez cet email.
    
    Cordialement,
    L'équipe Transpareo
    """
    
    send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])




def create_security_alert(user, alert_type, title, message, ip_address=None, location=None, device_info=None, severity='medium'):
    """Crée une alerte de sécurité"""
    # Convertir None en chaîne vide pour les champs qui ne supportent pas NULL
    location = location or ''
    if device_info:
        # Convertir device_info dict en JSON string si c'est un dict
        if isinstance(device_info, dict):
            import json
            device_info = json.dumps(device_info)
        device_info = device_info or ''
    else:
        device_info = ''
    
    SecurityAlert.objects.create(
        user=user,
        alert_type=alert_type,
        title=title,
        message=message,
        ip_address=ip_address,
        location=location,
        device_info=device_info,
        severity=severity
    )
    
    # Créer aussi une notification
    UserNotification.objects.create(
        user=user,
        notification_type='security',
        title=title,
        message=message,
        icon='🔒',
        action_url='/profile/'
    )


def check_and_award_badges(user):
    """Vérifie et attribue des badges à l'utilisateur"""
    badges_awarded = []
    
    # Badge "Premier pas" - Compte créé
    if not UserBadge.objects.filter(user=user, badge__name='Premier pas').exists():
        badge = Badge.objects.filter(name='Premier pas').first()
        if badge:
            UserBadge.objects.create(user=user, badge=badge)
            badges_awarded.append(badge)
    
    # Badge "Profil complet" - Profil complété à 100%
    if not UserBadge.objects.filter(user=user, badge__name='Profil complet').exists():
        if user.bio and user.avatar and user.ville:
            badge = Badge.objects.filter(name='Profil complet').first()
            if badge:
                UserBadge.objects.create(user=user, badge=badge)
                badges_awarded.append(badge)
    
    # Badge "Vérifié" - Email vérifié
    if user.email_verified and not UserBadge.objects.filter(user=user, badge__name='Vérifié').exists():
        badge = Badge.objects.filter(name='Vérifié').first()
        if badge:
            UserBadge.objects.create(user=user, badge=badge)
            badges_awarded.append(badge)
    
    # Badge "Double authentification" - 2FA activé
    if user.two_factor_enabled and not UserBadge.objects.filter(user=user, badge__name='Double authentification').exists():
        badge = Badge.objects.filter(name='Double authentification').first()
        if badge:
            UserBadge.objects.create(user=user, badge=badge)
            badges_awarded.append(badge)
    
    # Badge "Propriétaire vérifié" - Propriétaire vérifié
    if user.proprietaire_verified and not UserBadge.objects.filter(user=user, badge__name='Propriétaire vérifié').exists():
        badge = Badge.objects.filter(name='Propriétaire vérifié').first()
        if badge:
            UserBadge.objects.create(user=user, badge=badge)
            badges_awarded.append(badge)
    
    return badges_awarded


def create_notification(
    user, 
    notification_type, 
    title, 
    message, 
    icon='🔔', 
    action_url=None,
    from_user=None,
    related_post=None,
    related_comment=None,
    related_conversation=None,
    related_group=None,
    related_logement=None
):
    """Crée une notification pour l'utilisateur avec tous les champs"""
    # Vérifier les paramètres de notifications de l'utilisateur
    notification_settings = user.notification_settings or {}
    in_app_key = f'{notification_type}_in_app'
    
    # Vérifier si les notifications in-app sont activées (par défaut True)
    if not notification_settings.get(in_app_key, True):
        return None
    
    notification = UserNotification.objects.create(
        user=user,
        notification_type=notification_type,
        title=title,
        message=message,
        icon=icon,
        action_url=action_url,
        from_user=from_user,
        related_post=related_post,
        related_comment=related_comment,
        related_conversation=related_conversation,
        related_group=related_group,
        related_logement=related_logement
    )
    
    # Envoyer une notification push si activée
    push_key = f'{notification_type}_push'
    if notification_settings.get(push_key, True) and user.message_push_notifications:
        # TODO: Implémenter l'envoi de notification push navigateur
        pass
    
    # Envoyer un email si activé
    email_key = f'{notification_type}_email'
    if notification_settings.get(email_key, True) and user.message_email_notifications:
        # Vérifier la fréquence des emails
        if user.notification_email_frequency == 'immediate':
            # TODO: Envoyer email immédiatement (implémenter avec Celery pour ne pas bloquer)
            pass
        # Pour daily et weekly, utiliser un système de résumé (à implémenter avec Celery)
    
    return notification


def check_lease_notifications():
    """Vérifie et envoie les notifications automatiques pour les baux"""
    today = timezone.now().date()
    
    # Récupérer tous les baux actifs
    baux_actifs = Bail.objects.filter(statut='actif')
    
    for bail in baux_actifs:
        # 1. Notification loyer à payer (3 jours avant échéance)
        prochain_paiement_date = bail.get_prochain_paiement()
        jours_avant_echeance = (prochain_paiement_date - today).days
        
        if jours_avant_echeance == 3:
            # Vérifier si le paiement existe et n'est pas encore payé
            paiement = PaiementLoyer.objects.filter(
                bail=bail,
                date_echeance=prochain_paiement_date,
                statut__in=['en_attente', 'en_retard']
            ).first()
            
            if paiement:
                create_notification(
                    user=bail.locataire,
                    notification_type='system',
                    title='Rappel: Loyer à payer',
                    message=f"Votre loyer de {bail.get_montant_total_mensuel()}€ est à payer dans 3 jours (le {prochain_paiement_date.strftime('%d/%m/%Y')})",
                    icon='💰',
                    action_url=f'/connect/lease/?tab=payments',
                    related_logement=bail.logement
                )
        
        # 2. Notification assurance habitation à renouveler (1 mois avant)
        if bail.assurance_date_echeance:
            jours_avant_echeance_assurance = (bail.assurance_date_echeance - today).days
            
            if jours_avant_echeance_assurance == 30:
                create_notification(
                    user=bail.locataire,
                    notification_type='system',
                    title='Rappel: Assurance habitation à renouveler',
                    message=f"Votre assurance habitation expire dans 1 mois (le {bail.assurance_date_echeance.strftime('%d/%m/%Y')}). Pensez à la renouveler.",
                    icon='🛡️',
                    action_url=f'/connect/lease/?tab=contract',
                    related_logement=bail.logement
                )
        
        # 3. Notification fin de bail approchante (3 mois avant)
        if bail.date_fin:
            jours_avant_fin = (bail.date_fin - today).days
            
            if jours_avant_fin == 90:
                create_notification(
                    user=bail.locataire,
                    notification_type='system',
                    title='Rappel: Fin de bail dans 3 mois',
                    message=f"Votre bail se termine dans 3 mois (le {bail.date_fin.strftime('%d/%m/%Y')}). Pensez à organiser votre départ si vous souhaitez quitter.",
                    icon='📅',
                    action_url=f'/connect/lease/?tab=termination',
                    related_logement=bail.logement
                )
            
            # 4. Notification fin de bail approchante (1 mois avant)
            elif jours_avant_fin == 30:
                create_notification(
                    user=bail.locataire,
                    notification_type='system',
                    title='Rappel: Fin de bail dans 1 mois',
                    message=f"Votre bail se termine dans 1 mois (le {bail.date_fin.strftime('%d/%m/%Y')}). Assurez-vous d'avoir organisé votre départ.",
                    icon='📅',
                    action_url=f'/connect/lease/?tab=termination',
                    related_logement=bail.logement
                )
