"""
Module de sécurité et anti-fraude pour Transpareo Connect
Détection automatique de spam, arnaques et contenus inappropriés
"""
import re
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.http import JsonResponse


# ============================================
# LISTES DE DÉTECTION
# ============================================

# Mots-clés suspects (spam)
SPAM_KEYWORDS = [
    'cliquez ici', 'visitez notre site', 'gagnez de l\'argent',
    'travail à domicile', 'revenus passifs', 'opportunité unique',
    'offre limitée', 'n\'hésitez pas', 'contactez-nous rapidement',
    'gratuit', 'sans engagement', '100% garanti'
]

# Mots-clés liés aux arnaques
FRAUD_KEYWORDS = [
    'virement', 'western union', 'moneygram', 'transfert d\'argent',
    'avance de frais', 'frais de déblocage', 'payer d\'abord',
    'gagnez rapidement', 'investissement garanti', 'rendement exceptionnel',
    'prêt facile', 'crédit sans justificatif', 'argent facile',
    'bitcoin', 'cryptomonnaie', 'nft', 'pump and dump'
]

# Mots-clés inappropriés (insultes, violence)
INAPPROPRIATE_KEYWORDS = [
    'connard', 'salope', 'pute', 'fils de pute', 'enculé',
    'nique', 'foutre', 'merde', 'bordel', 'putain',
    'violence', 'tuer', 'mort', 'suicide', 'bombarde'
]

# Liens suspects (domaines de spam/phishing)
SUSPICIOUS_DOMAINS = [
    'bit.ly', 'tinyurl.com', 'short.link', 't.co',
    'goo.gl', 'ow.ly', 'is.gd', 'v.gd'
]

# Patterns de liens suspects
SUSPICIOUS_URL_PATTERN = re.compile(
    r'https?://(?:www\.)?([a-zA-Z0-9-]+\.(?:tk|ml|ga|cf|gq|xyz|top|click|download|site|online))',
    re.IGNORECASE
)


# ============================================
# DÉTECTION DE SPAM
# ============================================

def detect_spam(content, user=None):
    """
    Détecte si un contenu est du spam
    
    Returns:
        dict: {
            'is_spam': bool,
            'score': int (0-100),
            'reasons': list,
            'auto_quarantine': bool
        }
    """
    content_lower = content.lower()
    score = 0
    reasons = []
    
    # Vérifier les mots-clés spam
    spam_count = sum(1 for keyword in SPAM_KEYWORDS if keyword in content_lower)
    if spam_count > 0:
        score += spam_count * 10
        reasons.append(f"Contient {spam_count} mot(s)-clé(s) suspect(s)")
    
    # Vérifier les liens suspects
    suspicious_links = SUSPICIOUS_URL_PATTERN.findall(content)
    if suspicious_links:
        score += len(suspicious_links) * 15
        reasons.append(f"Contient {len(suspicious_links)} lien(s) suspect(s)")
    
    # Vérifier les liens raccourcis
    short_urls = [domain for domain in SUSPICIOUS_DOMAINS if domain in content_lower]
    if short_urls:
        score += len(short_urls) * 20
        reasons.append(f"Contient {len(short_urls)} lien(s) raccourci(s) suspect(s)")
    
    # Vérifier la répétition excessive
    words = content.split()
    if len(words) > 10:
        unique_words = set(words)
        repetition_ratio = 1 - (len(unique_words) / len(words))
        if repetition_ratio > 0.5:
            score += 30
            reasons.append("Répétition excessive de mots")
    
    # Vérifier les messages en majuscules (shouting)
    if len(content) > 10 and content.isupper():
        score += 15
        reasons.append("Message en majuscules (shouting)")
    
    is_spam = score >= 30
    auto_quarantine = score >= 50
    
    return {
        'is_spam': is_spam,
        'score': min(score, 100),
        'reasons': reasons,
        'auto_quarantine': auto_quarantine
    }


# ============================================
# DÉTECTION D'ARNAQUES
# ============================================

def detect_fraud(content, user=None):
    """
    Détecte si un contenu est une arnaque
    
    Returns:
        dict: {
            'is_fraud': bool,
            'score': int (0-100),
            'reasons': list,
            'alert_admin': bool
        }
    """
    content_lower = content.lower()
    score = 0
    reasons = []
    
    # Vérifier les mots-clés d'arnaque
    fraud_count = sum(1 for keyword in FRAUD_KEYWORDS if keyword in content_lower)
    if fraud_count > 0:
        score += fraud_count * 25
        reasons.append(f"Contient {fraud_count} mot(s)-clé(s) d'arnaque")
    
    # Vérifier les demandes d'argent hors plateforme
    money_patterns = [
        r'virement\s+(?:bancaire|urgent)',
        r'payer\s+(?:d\'abord|avant)',
        r'frais?\s+(?:de|à)\s+(?:déblocage|activation)',
        r'envoyer\s+de\s+l\'argent',
        r'transfert\s+d\'argent'
    ]
    
    for pattern in money_patterns:
        if re.search(pattern, content_lower):
            score += 30
            reasons.append("Demande d'argent suspecte")
            break
    
    # Vérifier les offres trop bonnes pour être vraies
    if any(phrase in content_lower for phrase in ['gagnez rapidement', 'rendement garanti', '100% sûr']):
        score += 20
        reasons.append("Offre suspecte (trop belle pour être vraie)")
    
    is_fraud = score >= 30
    alert_admin = score >= 40
    
    return {
        'is_fraud': is_fraud,
        'score': min(score, 100),
        'reasons': reasons,
        'alert_admin': alert_admin
    }


# ============================================
# DÉTECTION DE CONTENUS INAPPROPRIÉS
# ============================================

def detect_inappropriate(content, user=None):
    """
    Détecte si un contenu est inapproprié (insultes, violence)
    
    Returns:
        dict: {
            'is_inappropriate': bool,
            'score': int (0-100),
            'reasons': list,
            'auto_quarantine': bool
        }
    """
    content_lower = content.lower()
    score = 0
    reasons = []
    
    # Vérifier les mots-clés inappropriés
    inappropriate_count = sum(1 for keyword in INAPPROPRIATE_KEYWORDS if keyword in content_lower)
    if inappropriate_count > 0:
        score += inappropriate_count * 20
        reasons.append(f"Contient {inappropriate_count} mot(s) inapproprié(s)")
    
    # Vérifier les menaces
    threat_patterns = [
        r'je\s+(?:vais|vais\s+te)\s+(?:tuer|frapper|attaquer)',
        r'(?:mort|suicide|violence)',
    ]
    
    for pattern in threat_patterns:
        if re.search(pattern, content_lower):
            score += 40
            reasons.append("Contient des menaces ou références à la violence")
            break
    
    is_inappropriate = score >= 20
    auto_quarantine = score >= 50
    
    return {
        'is_inappropriate': is_inappropriate,
        'score': min(score, 100),
        'reasons': reasons,
        'auto_quarantine': auto_quarantine
    }


# ============================================
# DÉTECTION GLOBALE
# ============================================

def detect_suspicious_content(content, user=None):
    """
    Détecte tout type de contenu suspect (spam, arnaque, inapproprié)
    
    Returns:
        dict: {
            'is_suspicious': bool,
            'spam': dict,
            'fraud': dict,
            'inappropriate': dict,
            'max_score': int,
            'should_quarantine': bool,
            'should_alert_admin': bool
        }
    """
    spam_result = detect_spam(content, user)
    fraud_result = detect_fraud(content, user)
    inappropriate_result = detect_inappropriate(content, user)
    
    max_score = max(
        spam_result['score'],
        fraud_result['score'],
        inappropriate_result['score']
    )
    
    is_suspicious = (
        spam_result['is_spam'] or
        fraud_result['is_fraud'] or
        inappropriate_result['is_inappropriate']
    )
    
    should_quarantine = (
        spam_result['auto_quarantine'] or
        inappropriate_result['auto_quarantine']
    )
    
    should_alert_admin = (
        fraud_result['alert_admin'] or
        max_score >= 60
    )
    
    return {
        'is_suspicious': is_suspicious,
        'spam': spam_result,
        'fraud': fraud_result,
        'inappropriate': inappropriate_result,
        'max_score': max_score,
        'should_quarantine': should_quarantine,
        'should_alert_admin': should_alert_admin
    }


# ============================================
# DÉTECTION DE BOTS
# ============================================

def detect_bot_user(user):
    """
    Détecte si un utilisateur est probablement un bot
    
    Criteria:
    - Compte créé récemment (< 24h)
    - Pas d'avatar
    - Pas de bio
    - Nom d'utilisateur suspect (chiffres aléatoires)
    - Aucune activité normale
    
    Returns:
        dict: {
            'is_bot': bool,
            'score': int (0-100),
            'reasons': list
        }
    """
    if not user or not user.is_authenticated:
        return {'is_bot': False, 'score': 0, 'reasons': []}
    
    score = 0
    reasons = []
    
    # Compte récent (< 24h)
    if user.date_joined > timezone.now() - timedelta(hours=24):
        score += 20
        reasons.append("Compte créé il y a moins de 24h")
    
    # Pas d'avatar
    if not user.avatar:
        score += 10
        reasons.append("Pas d'avatar")
    
    # Pas de bio
    if not user.bio:
        score += 10
        reasons.append("Pas de biographie")
    
    # Nom d'utilisateur suspect (beaucoup de chiffres)
    if re.match(r'^[a-zA-Z]*\d{5,}', user.username):
        score += 25
        reasons.append("Nom d'utilisateur suspect (trop de chiffres)")
    
    # Email suspect (provisoire, jetable)
    disposable_emails = ['tempmail', 'guerrillamail', 'mailinator', '10minutemail']
    if any(domain in user.email.lower() for domain in disposable_emails):
        score += 30
        reasons.append("Email provisoire/jetable suspect")
    
    # Pas d'email vérifié
    if not user.email_verified:
        score += 15
        reasons.append("Email non vérifié")
    
    is_bot = score >= 50
    
    return {
        'is_bot': is_bot,
        'score': min(score, 100),
        'reasons': reasons
    }


# ============================================
# RATE LIMITING AVANCÉ
# ============================================

def check_rate_limit(user, action_type, limit, window_seconds=3600):
    """
    Vérifie si un utilisateur a dépassé la limite de rate pour une action
    
    Args:
        user: Utilisateur Django
        action_type: Type d'action ('post', 'message', 'connection_request')
        limit: Nombre maximum d'actions autorisées
        window_seconds: Fenêtre de temps en secondes (défaut: 1h)
    
    Returns:
        dict: {
            'allowed': bool,
            'remaining': int,
            'reset_at': datetime
        }
    """
    if not user or not user.is_authenticated:
        return {'allowed': False, 'remaining': 0, 'reset_at': None}
    
    cache_key = f'rate_limit_{action_type}_{user.id}'
    current_count = cache.get(cache_key, 0)
    
    if current_count >= limit:
        ttl = cache.ttl(cache_key)
        reset_at = timezone.now() + timedelta(seconds=ttl if ttl else window_seconds)
        return {
            'allowed': False,
            'remaining': 0,
            'reset_at': reset_at
        }
    
    # Incrémenter le compteur
    cache.set(cache_key, current_count + 1, window_seconds)
    
    return {
        'allowed': True,
        'remaining': limit - (current_count + 1),
        'reset_at': timezone.now() + timedelta(seconds=window_seconds)
    }


# ============================================
# LIMITES PAR DÉFAUT
# ============================================

# Limites de rate par action (par jour)
RATE_LIMITS = {
    'post': 10,  # Max 10 posts par jour
    'message': 20,  # Max 20 messages par jour
    'connection_request': 50,  # Max 50 demandes de connexion par jour
    'comment': 50,  # Max 50 commentaires par jour
}


def check_action_rate_limit(user, action_type):
    """Vérifie les limites de rate pour une action spécifique"""
    limit = RATE_LIMITS.get(action_type, 10)
    return check_rate_limit(user, action_type, limit, window_seconds=86400)  # 24h

