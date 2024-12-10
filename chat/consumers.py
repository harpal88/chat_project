import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils.text import slugify
from uuid import uuid4
from .models import ChatMessage

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Fetch and send messages ordered by time
        messages = await self.get_messages_ordered_by_time()
        current_date = None
        for message in messages:
            message_date = message['timestamp'].strftime('%Y-%m-%d')  # Extract date
            message_time = message['timestamp'].strftime('%H:%M')     # Extract time

            # Send date as a separate message if it's a new day
            if current_date != message_date:
                await self.send(text_data=json.dumps({
                    'type': 'date',
                    'date': message_date
                }))
                current_date = message_date

            # Send each message
            await self.send(text_data=json.dumps({
                'type': 'message',
                'username': message['user__username'],
                'time': message_time,
                'message': message['message'],
                'file_url': message['file']
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get('message', '')
        file_url = data.get('file', None)

        if not message and not file_url:
            return

        chat_message = await self.save_message(self.room_name, self.scope["user"], message, file_url)

        if chat_message is None:
            print("Error: Message was not saved.")
            return

        message_time = chat_message.timestamp.strftime('%H:%M')

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': self.scope['user'].username,
                'time': message_time,
                'message': message if message else '',
                'file_url': file_url
            }
        )

    async def chat_message(self, event):
        file_url = None
        if event.get('file_url'):
            # Ensure no double prefixing of MEDIA_URL
            if not event['file_url'].startswith(settings.MEDIA_URL):
                file_url = f"{settings.MEDIA_URL}{event['file_url']}"
            else:
                file_url = event['file_url']

        await self.send(text_data=json.dumps({
            'type': 'message',
            'username': event['username'],
            'time': event['time'],
            'message': event['message'],
            'file_url': file_url  # Corrected file URL
        }))

    @database_sync_to_async
    def get_messages_ordered_by_time(self):
            """
            Fetch messages from the database ordered by timestamp in ascending order.
            """
            return list(ChatMessage.objects.filter(room_name=self.room_name)
                        .select_related('user')  # Optimize database query
                        .order_by('timestamp')  # Fetch messages in ascending order
                        .values('user__username', 'message', 'timestamp', 'file'))

    @database_sync_to_async
    def save_message(self, room_name, user, message, file_url):
        if file_url and not isinstance(file_url, str):
            file_url.name = self.clean_file_name(file_url.name)  # Sanitize file name
            print(f"Sanitized file name: {file_url.name}")
        else:
            print(f"Using provided file URL: {file_url}")

        # Check if file is being saved correctly
        print(f"Saving file to media/chat_files/: {file_url}")
        
        return ChatMessage.objects.create(
            room_name=room_name,
            user=user,
            message=message,
            file=file_url
        )



    def clean_file_name(self, file_name):
        base, ext = os.path.splitext(file_name)
        return f"{slugify(base)}-{uuid4().hex[:8]}{ext}"

