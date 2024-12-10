from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('chat.urls')),  # Include app-specific URLs
        path('chat/', include('chat.urls')),  # Include the chat app URLs

]
