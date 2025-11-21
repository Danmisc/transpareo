#!/usr/bin/env python
"""
Script simple pour supprimer toutes les conversations et messages
Utilisation: python delete_conversations.py
"""
import os
import sys
import django

# Configuration Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from core.models import Conversation, Message

def delete_all_conversations():
    """Supprime toutes les conversations et messages"""
    # Compter avant suppression
    conversation_count = Conversation.objects.count()
    message_count = Message.objects.count()
    
    print(f"📊 Statistiques avant suppression:")
    print(f"   - Conversations: {conversation_count}")
    print(f"   - Messages: {message_count}")
    
    if conversation_count == 0 and message_count == 0:
        print("✅ Aucune conversation ou message à supprimer.")
        return
    
    # Demander confirmation
    response = input(f"\n⚠️  Êtes-vous sûr de vouloir supprimer {conversation_count} conversation(s) et {message_count} message(s) ? (oui/non): ")
    if response.lower() not in ['oui', 'o', 'yes', 'y']:
        print("❌ Suppression annulée.")
        return
    
    # Supprimer tous les messages d'abord (pour éviter les erreurs de clé étrangère)
    Message.objects.all().delete()
    print(f"✅ {message_count} message(s) supprimé(s)")
    
    # Supprimer toutes les conversations
    Conversation.objects.all().delete()
    print(f"✅ {conversation_count} conversation(s) supprimée(s)")
    
    print("\n🎉 Toutes les conversations et messages ont été supprimés avec succès !")

if __name__ == '__main__':
    delete_all_conversations()

