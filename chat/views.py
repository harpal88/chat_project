import os
import traceback
from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status

from .models import Comment, Message, Group
from .serializers import CommentSerializer

# ----------- General Views -----------
def home(request):
    """Render the chat home page."""
    return render(request, 'chat.html')

@login_required
def dashboard(request):
    """Render the dashboard page with chat messages."""
    messages = Message.objects.all()
    return render(request, 'dashboard.html', {'user': request.user, 'messages': messages})

def group_list(request):
    """Render a list of chat groups."""
    groups = Group.objects.all()
    return render(request, 'group_list.html', {'groups': groups})

# ----------- Authentication-Related Actions -----------
def logout_success(request):
    """Handle user logout and redirect to login page."""
    logout(request)
    return redirect('login')

# ----------- API Views -----------
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

class CommentListView(APIView):
    """API view to list and create comments."""
    def get(self, request):
        comments = Comment.objects.all()
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_exempt, name='dispatch')
class FileUploadView(View):
    """Handle file uploads for chat."""
    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return JsonResponse({'error': 'No file uploaded'}, status=400)

        # Save the file to media/chat_files/
        file_path = default_storage.save(
            os.path.join('chat_files', file.name),
            ContentFile(file.read())
        )
        return JsonResponse({'file_url': f'{settings.MEDIA_URL}{file_path}'}, status=200)
