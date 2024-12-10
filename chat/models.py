from django.db import models
from django.contrib.auth.models import User


class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(User, related_name='custom_groups')

    def __str__(self):
        return self.name


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField(null=True, blank=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.user.username} in {self.group.name}"


class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]


from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    room_name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True)  # Allow empty messages for file-only chats
    timestamp = models.DateTimeField(auto_now_add=True)
    file = models.FileField(upload_to='chat_files/', null=True, blank=True)
    read_by = models.ManyToManyField(User, related_name='read_messages', blank=True)  # Tracks users who read the message

    def __str__(self):
        if self.message and self.file:
            return f"[{self.timestamp}] {self.user.username}: {self.message} (File attached)"
        elif self.message:
            return f"[{self.timestamp}] {self.user.username}: {self.message}"
        elif self.file:
            return f"[{self.timestamp}] {self.user.username}: File attached"
        else:
            return f"[{self.timestamp}] {self.user.username}: (Empty message)"

