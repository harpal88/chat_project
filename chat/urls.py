from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from . import views
from .views import FileUploadView, UploadCommentView, logout_success, CommentListView

urlpatterns = [
    # General Views
    path('', views.home, name='dashboard'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name='logout.html'), name='logout'),
    path('logout_success/', logout_success, name='logout_success'),


    # API Endpoints
    path('upload/comment/', UploadCommentView.as_view(), name='upload_comment'),
    path('comments/', CommentListView.as_view(), name='comment_list'),
    path('api/upload-file/', FileUploadView.as_view(), name='upload_file'),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
