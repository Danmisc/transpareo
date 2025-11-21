"""
Adapter personnalisé pour django-allauth
Gère les redirections après connexion OAuth
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.conf import settings
from django.contrib.auth import login
from django.contrib import messages
from django.urls import reverse


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """Adapter personnalisé pour les comptes sociaux"""
    
    def pre_social_login(self, request, sociallogin):
        """Appelé avant la connexion sociale"""
        # Si l'utilisateur existe déjà avec cet email, connecter directement
        if sociallogin.is_existing:
            return
        
        # Vérifier si un compte existe avec cet email
        email = sociallogin.account.extra_data.get('email')
        if email:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(email=email)
                # Connecter le compte social à l'utilisateur existant
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass
    
    def save_user(self, request, sociallogin, form=None):
        """Sauvegarde l'utilisateur après connexion sociale"""
        user = super().save_user(request, sociallogin, form)
        
        # Marquer l'email comme vérifié pour les comptes sociaux
        if user and not user.email_verified:
            user.email_verified = True
            user.save()
        
        # Vérifier et attribuer des badges
        if user:
            from .auth_utils import check_and_award_badges, create_notification
            badges = check_and_award_badges(user)
            if badges:
                for badge in badges:
                    create_notification(
                        user, 'activity',
                        f'Nouveau badge débloqué !',
                        f'Vous avez obtenu le badge "{badge.name}"',
                        badge.icon
                    )
        
        return user
    
    def get_connect_redirect_url(self, request, socialaccount):
        """URL de redirection après connexion d'un compte social"""
        # Résoudre l'URL si c'est un nom d'URL, sinon retourner tel quel
        redirect_url = settings.LOGIN_REDIRECT_URL
        if redirect_url and not redirect_url.startswith('/') and not redirect_url.startswith('http'):
            try:
                return reverse(redirect_url)
            except:
                return '/'
        return redirect_url or '/'
    
    def get_login_redirect_url(self, request):
        """URL de redirection après connexion sociale"""
        # Résoudre l'URL si c'est un nom d'URL, sinon retourner tel quel
        redirect_url = settings.LOGIN_REDIRECT_URL
        if redirect_url and not redirect_url.startswith('/') and not redirect_url.startswith('http'):
            try:
                return reverse(redirect_url)
            except:
                return '/'
        return redirect_url or '/'


class CustomAccountAdapter(DefaultAccountAdapter):
    """Adapter personnalisé pour les comptes normaux"""
    
    def get_login_redirect_url(self, request):
        """URL de redirection après connexion"""
        # Résoudre l'URL si c'est un nom d'URL, sinon retourner tel quel
        redirect_url = settings.LOGIN_REDIRECT_URL
        if redirect_url and not redirect_url.startswith('/') and not redirect_url.startswith('http'):
            try:
                return reverse(redirect_url)
            except:
                return '/'
        return redirect_url or '/'
    
    def get_signup_redirect_url(self, request):
        """URL de redirection après inscription"""
        # Résoudre l'URL si c'est un nom d'URL, sinon retourner tel quel
        redirect_url = settings.LOGIN_REDIRECT_URL
        if redirect_url and not redirect_url.startswith('/') and not redirect_url.startswith('http'):
            try:
                return reverse(redirect_url)
            except:
                return '/'
        return redirect_url or '/'

