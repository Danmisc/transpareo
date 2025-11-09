from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import uuid
from user_agents import parse


def get_client_ip(request):
    """Récupère l'IP du client"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_device_info(request):
    """Récupère les informations du device"""
    user_agent_string = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse(user_agent_string)
    
    return {
        'user_agent': user_agent_string,
        'device_type': 'Mobile' if user_agent.is_mobile else 'Tablet' if user_agent.is_tablet else 'Desktop',
        'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}",
        'os': f"{user_agent.os.family} {user_agent.os.version_string}",
        'device_name': f"{user_agent.device.family}"
    }


def send_verification_email(user, token):
    """Envoie l'email de vérification"""
    verification_url = f"{settings.SITE_URL}/verify-email/{token}/"
    
    subject = "Vérifiez votre email - Transpareo"
    message = f"""
    Bonjour {user.username},
    
    Merci de vous être inscrit sur Transpareo !
    
    Pour activer votre compte, veuillez cliquer sur le lien ci-dessous :
    {verification_url}
    
    Ce lien expirera dans 24 heures.
    
    Si vous n'avez pas créé de compte, ignorez cet email.
    
    Cordialement,
    L'équipe Transpareo
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def send_password_reset_email(user, token):
    """Envoie l'email de réinitialisation"""
    reset_url = f"{settings.SITE_URL}/reset-password/{token}/"
    
    subject = "Réinitialisation de votre mot de passe - Transpareo"
    message = f"""
    Bonjour {user.username},
    
    Vous avez demandé à réinitialiser votre mot de passe.
    
    Cliquez sur le lien ci-dessous pour créer un nouveau mot de passe :
    {reset_url}
    
    Ce lien expirera dans 1 heure.
    
    Si vous n'avez pas demandé cette réinitialisation, ignorez cet email.
    Votre mot de passe actuel restera inchangé.
    
    Cordialement,
    L'équipe Transpareo
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )


def create_email_verification_token(user):
    """Crée un token de vérification email"""
    from core.models import EmailVerificationToken
    
    token = EmailVerificationToken.objects.create(
        user=user,
        expires_at=timezone.now() + timedelta(hours=24)
    )
    return token


def create_password_reset_token(user, ip_address):
    """Crée un token de réinitialisation"""
    from core.models import PasswordResetToken
    
    token = PasswordResetToken.objects.create(
        user=user,
        ip_address=ip_address,
        expires_at=timezone.now() + timedelta(hours=1)
    )
    return token


def log_login_attempt(user, request, success=True, reason=''):
    """Enregistre une tentative de connexion"""
    from core.models import LoginHistory
    
    ip = get_client_ip(request)
    device_info = get_device_info(request)
    
    LoginHistory.objects.create(
        user=user,
        ip_address=ip,
        user_agent=device_info['user_agent'],
        device_type=device_info['device_type'],
        browser=device_info['browser'],
        os=device_info['os'],
        success=success,
        reason=reason
    )


def create_user_session(user, request):
    """Crée une session utilisateur"""
    from core.models import UserSession
    
    ip = get_client_ip(request)
    device_info = get_device_info(request)
    
    # Marquer toutes les autres sessions comme non-courantes
    UserSession.objects.filter(user=user).update(is_current=False)
    
    session = UserSession.objects.create(
        user=user,
        session_key=request.session.session_key,
        ip_address=ip,
        user_agent=device_info['user_agent'],
        device_name=device_info['device_name'],
        browser=device_info['browser'],
        os=device_info['os'],
        is_current=True
    )
    return session


def check_suspicious_login(user, request):
    """Vérifie si la connexion est suspecte"""
    from core.models import LoginHistory
    
    ip = get_client_ip(request)
    device_info = get_device_info(request)
    
    # Vérifier l'historique récent
    recent_logins = LoginHistory.objects.filter(
        user=user,
        success=True,
        timestamp__gte=timezone.now() - timedelta(days=30)
    )
    
    if not recent_logins.exists():
        return False  # Première connexion
    
    # Vérifier si IP nouvelle
    known_ips = recent_logins.values_list('ip_address', flat=True).distinct()
    if ip not in known_ips:
        return True  # IP inconnue
    
    # Vérifier si device nouveau
    known_devices = recent_logins.values_list('device_type', flat=True).distinct()
    if device_info['device_type'] not in known_devices:
        return True  # Device inconnu
    
    return False
