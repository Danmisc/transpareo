"""
Rate limiting utility pour sécuriser les formulaires
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.conf import settings
from functools import wraps
import time


def rate_limit(key_func, limit=5, window=300, message="Trop de tentatives. Veuillez réessayer plus tard."):
    """
    Décorateur de rate limiting
    
    Args:
        key_func: Fonction qui retourne la clé de cache (généralement basée sur l'IP)
        limit: Nombre maximum de tentatives
        window: Fenêtre de temps en secondes (défaut: 5 minutes)
        message: Message d'erreur à afficher
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Générer les clés de cache
            cache_key = f"rate_limit:{key_func(request)}"
            timestamp_key = f"rate_limit_ts:{key_func(request)}"
            
            # Récupérer le nombre de tentatives et le timestamp
            attempts = cache.get(cache_key, 0)
            timestamp = cache.get(timestamp_key, 0)
            
            if attempts >= limit:
                # Calculer le temps restant
                current_time = time.time()
                if timestamp > 0:
                    elapsed = current_time - timestamp
                    remaining = window - elapsed
                    if remaining < 0:
                        remaining = 0
                    ttl = int(remaining)
                else:
                    ttl = window
                
                from django.contrib import messages
                minutes = max(1, (ttl // 60) + 1) if ttl > 0 else 1
                messages.error(request, f"{message} Réessayez dans {minutes} minute(s).")
                
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({
                        'error': message,
                        'retry_after': ttl
                    }, status=429)
                
                # Re-rendre le formulaire avec l'erreur
                from django.shortcuts import render
                from .forms import LoginForm, SignupForm
                
                # Déterminer le formulaire approprié
                if 'login' in request.path:
                    form = LoginForm()
                    template = 'core/login_modern.html'
                elif 'signup' in request.path:
                    form = SignupForm()
                    template = 'core/signup_modern.html'
                else:
                    form = None
                    template = 'core/login_modern.html'
                
                return render(request, template, {
                    'form': form,
                    'rate_limited': True
                })
            
            # Si c'est la première tentative ou si le timestamp n'existe pas, créer un nouveau
            if timestamp == 0:
                timestamp = time.time()
                cache.set(timestamp_key, timestamp, window + 60)  # Stocker 1 minute de plus pour la sécurité
            
            # Incrémenter le compteur
            cache.set(cache_key, attempts + 1, window)
            
            # Exécuter la vue
            response = view_func(request, *args, **kwargs)
            
            # Si succès, réinitialiser le compteur
            if hasattr(response, 'status_code') and response.status_code in [200, 302]:
                if hasattr(request, 'user') and request.user.is_authenticated:
                    cache.delete(cache_key)
                    cache.delete(timestamp_key)
            
            return response
        return wrapper
    return decorator


def get_client_ip_key(request):
    """Retourne l'IP du client comme clé de rate limiting"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


def get_email_key(request):
    """Retourne l'email comme clé de rate limiting"""
    email = request.POST.get('username') or request.POST.get('email', '')
    return email.lower() if email else get_client_ip_key(request)

