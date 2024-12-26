import os
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.conf import settings
from django.utils.text import slugify
from uuid import uuid4
from .models import ChatMessage
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
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
            print("No message or file provided.")
            return

        # Save the message
        chat_message = await self.save_message(self.room_name, self.scope["user"], message, file_url)

        # Send the saved message to the room group
        if chat_message:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'username': self.scope["user"].username,
                    'message': message,
                    'file_url': f"{settings.MEDIA_URL}{chat_message.file}" if chat_message.file else None,
                    'time': chat_message.timestamp.strftime('%H:%M'),
                }
            )

    async def chat_message(self, event):
            """
            Handle the `chat_message` type event.
            """
            file_url = None
            if event.get('file_url'):
                # Ensure MEDIA_URL is prepended
                if not event['file_url'].startswith(settings.MEDIA_URL):
                    file_url = f"{settings.MEDIA_URL}{event['file_url']}"
                else:
                    file_url = event['file_url']

            # Send message to WebSocket
            await self.send(text_data=json.dumps({
                'type': 'message',
                'username': event['username'],
                'time': event['time'],
                'message': event['message'],
                'file_url': file_url
            }))






    
    @database_sync_to_async
    def get_messages_ordered_by_time(self):
        messages = ChatMessage.objects.filter(room_name=self.room_name).select_related('user').order_by('timestamp')
        result = [
            {
                'user__username': msg.user.username,
                'message': msg.message,
                'timestamp': msg.timestamp,
                'file': f"{settings.MEDIA_URL}{msg.file}" if msg.file else None
            }
            for msg in messages
        ]
        print("Messages sent to frontend:", result)  # Debug log
        return result





    @database_sync_to_async
    def save_message(self, room_name, user, message, file):
        if file and not isinstance(file, str):  # Check if it's a file object
            file.name = self.clean_file_name(file.name)  # Sanitize file name
            file_path = default_storage.save(os.path.join('chat_files', file.name), ContentFile(file.read()))
            print(f"File saved to: {file_path}")
            file = file_path  # Update file to the saved path

        elif isinstance(file, str) and file.startswith(settings.MEDIA_URL):
            # Strip MEDIA_URL to save only the relative path
            file = file.replace(settings.MEDIA_URL, '').lstrip('/')

        print(f"Final file value to save in database: {file}")
        return ChatMessage.objects.create(
            room_name=room_name,
            user=user,
            message=message,
            file=file or None  # Save None if no file
        )








    def clean_file_name(file_name):
        import os
        from django.utils.text import slugify
        from uuid import uuid4

        base, ext = os.path.splitext(file_name)
        return f"{slugify(base)}-{uuid4().hex[:8]}{ext}"
class LogoutConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope["user"].is_authenticated:
            self.group_name = f"user_{self.scope['user'].id}"
            await self.channel_layer.group_add(self.group_name, self.channel_name)
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def force_logout(self, event):
        # Close the WebSocket connection and redirect
        await self.send(text_data=json.dumps({"type": "force_logout"}))
        await self.close()
