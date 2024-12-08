from django.db import models
from django.contrib.auth.models import User

from django.contrib.auth.models import User
from django.db import models

class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    members = models.ManyToManyField(
        User,
        related_name='custom_groups',  # Avoids conflict with 'auth.User.groups'
    )

    def __str__(self):
        return self.name


from django.db import models
from django.contrib.auth.models import User

class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField(blank=True)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)


from django.db import models

class Comment(models.Model):
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.text[:50]
