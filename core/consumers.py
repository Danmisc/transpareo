"""
WebSocket consumers pour les messages en temps réel
"""
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from .models import Message, Conversation, MessageReaction, Call


class MessageConsumer(AsyncWebsocketConsumer):
    """Consumer pour les messages en temps réel"""
    
    async def connect(self):
        """Connexion WebSocket"""
        self.user = self.scope["user"]
        
        if self.user.is_anonymous:
            await self.close()
            return
        
        self.user_id = self.user.id
        self.conversation_id = self.scope['url_route']['kwargs'].get('conversation_id')
        
        # Rejoindre le groupe de la conversation
        if self.conversation_id:
            self.room_group_name = f'messages_{self.conversation_id}'
        else:
            self.room_group_name = f'user_{self.user_id}'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Envoyer confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connecté au WebSocket'
        }))
    
    async def disconnect(self, close_code):
        """Déconnexion WebSocket"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recevoir un message du WebSocket"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                # S'abonner à une conversation
                conversation_id = data.get('conversation_id')
                if conversation_id:
                    await self.subscribe_to_conversation(conversation_id)
            
            elif message_type == 'typing':
                # Indicateur de frappe
                conversation_id = data.get('conversation_id')
                is_typing = data.get('is_typing', False)
                await self.handle_typing(conversation_id, is_typing)
            
            elif message_type == 'new_message':
                # Nouveau message (pour debug, normalement via API)
                await self.handle_new_message(data)
            
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Format JSON invalide'
            }))
    
    async def subscribe_to_conversation(self, conversation_id):
        """S'abonner à une conversation"""
        # Vérifier que l'utilisateur a accès à la conversation
        has_access = await self.check_conversation_access(conversation_id)
        
        if has_access:
            room_group_name = f'messages_{conversation_id}'
            await self.channel_layer.group_add(
                room_group_name,
                self.channel_name
            )
            
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'conversation_id': conversation_id
            }))
    
    async def handle_typing(self, conversation_id, is_typing):
        """Gérer l'indicateur de frappe"""
        room_group_name = f'messages_{conversation_id}'
        
        await self.channel_layer.group_send(
            room_group_name,
            {
                'type': 'typing_indicator',
                'user_id': self.user_id,
                'username': self.user.username,
                'is_typing': is_typing,
                'conversation_id': conversation_id
            }
        )
    
    async def handle_new_message(self, data):
        """Gérer un nouveau message (pour debug)"""
        # Normalement, les messages sont créés via l'API et diffusés via signals
        pass
    
    async def typing_indicator(self, event):
        """Envoyer l'indicateur de frappe"""
        await self.send(text_data=json.dumps({
            'type': 'typing',
            'user_id': event['user_id'],
            'username': event['username'],
            'is_typing': event['is_typing'],
            'conversation_id': event['conversation_id']
        }))
    
    async def new_message(self, event):
        """Envoyer un nouveau message"""
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': event['message']
        }))
    
    async def message_reaction(self, event):
        """Envoyer une réaction à un message"""
        await self.send(text_data=json.dumps({
            'type': 'reaction',
            'reaction': event['reaction']
        }))
    
    async def call_event(self, event):
        """Envoyer un événement d'appel"""
        await self.send(text_data=json.dumps({
            'type': 'call',
            'call': event['call']
        }))
    
    @database_sync_to_async
    def check_conversation_access(self, conversation_id):
        """Vérifier l'accès à une conversation"""
        try:
            conversation = Conversation.objects.get(id=conversation_id)
            return self.user in conversation.participants.all()
        except Conversation.DoesNotExist:
            return False

