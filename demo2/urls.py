"""
URL configuration for demo2 project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('django-admin/', admin.site.urls),           # Changed from 'admin/' to 'django-admin/'
    path('', include('reservations.urls')),           # Your app routes (includes /admin/)
    path('accounts/', include('django.contrib.auth.urls')),  # Django auth system
]
