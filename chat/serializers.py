from rest_framework import serializers
from .models import Comment  # Import only Comment model

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'text', 'created_at']  # Include only necessary fields
