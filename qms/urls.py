"""
URL configuration for qms project.
"""
from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('users/', include('apps.users.urls')),
    path('products/', include('apps.products.urls')),
    path('quality/', include('apps.quality.urls')),
    path('testing/', include('apps.testing.urls')),
    path('analytics/', include('apps.analytics.urls')),
]
