"""
Context processors pour Transpareo Connect
Ajoute les compteurs de notifications et messages à tous les templates
"""
from .models import (
    UserNotification, Conversation, Message,
    SignalementPost, SignalementCommentaire, SignalementMessage, SignalementGroupe,
    VerificationRequest
)


def connect_context(request):
    """Ajoute les compteurs de notifications et messages à tous les templates"""
    context = {
        'unread_notifications_count': 0,
        'unread_messages_count': 0,
    }
    
    if request.user.is_authenticated:
        # Compter les notifications non lues
        context['unread_notifications_count'] = UserNotification.objects.filter(
            user=request.user,
            read=False
        ).count()
        
        # Compter les messages non lus dans les conversations de l'utilisateur
        conversations = Conversation.objects.filter(participants=request.user)
        if conversations.exists():
            unread_messages = Message.objects.filter(
                conversation__in=conversations,
                read=False
            ).exclude(sender=request.user)
            context['unread_messages_count'] = unread_messages.count()
        else:
            context['unread_messages_count'] = 0
    
    return context


def admin_context(request):
    """Ajoute les compteurs admin (signalements, vérifications) aux templates admin"""
    context = {
        'signalements_en_attente': 0,
        'verifications_en_attente': 0,
    }
    
    # Vérifier si l'utilisateur est admin et si on est sur une page admin
    if request.user.is_authenticated and request.user.is_staff:
        # Vérifier si on est sur une page admin
        if request.path.startswith('/connect-admin/'):
            # Compter les signalements en attente
            context['signalements_en_attente'] = (
                SignalementPost.objects.filter(statut='en_attente').count() +
                SignalementCommentaire.objects.filter(statut='en_attente').count() +
                SignalementMessage.objects.filter(statut='en_attente').count() +
                SignalementGroupe.objects.filter(statut='en_attente').count()
            )
            
            # Compter les vérifications en attente
            context['verifications_en_attente'] = VerificationRequest.objects.filter(
                status='pending'
            ).count()
    
    return context

