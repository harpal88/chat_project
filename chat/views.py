from django.shortcuts import render

def home(request):
    return render(request, 'chat.html')

def home(request, room_name="default-room"):
    return render(request, 'chat.html', {'room_name': room_name})

import os
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Comment
from .serializers import CommentSerializer

# app/views.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import render


# ----------- General Views -----------

from django.shortcuts import render
from .models import Message  # Import your chat message model

from django.shortcuts import render
from .models import Message



@login_required
def profile(request):
    """Render the profile page for the logged-in user."""
    return render(request, 'profile.html', {'user': request.user})


def register(request):
    """Handle user registration."""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})


# ----------- Authentication-Related Actions -----------

def logout_success(request):
    """Log out the user."""
    logout(request)
    return redirect('login')  # Redirect to the login page


# ----------- API Views -----------
import traceback

class UploadCommentView(APIView):
    """API view to handle comment uploads."""
    def post(self, request, *args, **kwargs):
        try:
            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            traceback.print_exc()  # Log the exception
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Comment
from .serializers import CommentSerializer

class CommentListView(APIView):
    """API view to list all chat messages."""
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        """API view to create a new chat message."""
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.shortcuts import render
from .models import Message

def dashboard(request):
    messages = Message.objects.all()
    return render(request, 'dashboard.html', {'user': request.user, 'messages': messages})

from django.shortcuts import render
from chat.models import Group,Message

def group_list(request):
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})


