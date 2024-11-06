import json
from channels.generic.websocket import AsyncWebsocketConsumer
from users.models import Message
from django.contrib.auth import get_user_model
from asgiref.sync import sync_to_async

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Rejoindre la salle
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Quitter la salle
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        sender_username = self.scope['user'].username

        # Sauvegarder le message dans la base de données
        sender = await self.get_user(sender_username)
        recipient = await self.get_user(self.room_name)
        if sender and recipient:
            await self.save_message(sender, recipient, message)

        # Envoyer le message à la salle
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender_username
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']

        # Envoyer le message à WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender
        }))

    @sync_to_async
    def get_user(self, username):
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None

    @sync_to_async
    def save_message(self, sender, recipient, message):
        # Crée un nouveau message dans la base de données
        Message.objects.create(
            sender=sender,
            recipient=recipient,
            content=message
        )
