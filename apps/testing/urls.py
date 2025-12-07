"""
URL configuration for testing app.
"""
from django.urls import path
from . import views

app_name = 'testing'

urlpatterns = [
    path('', views.TestRequestListView.as_view(), name='list'),
    path('pipeline/start/', views.pipeline_start, name='pipeline_start'),
    path('pipeline/<uuid:test_id>/step/<int:step>/', views.pipeline_step, name='pipeline_step'),
    path('<uuid:test_id>/', views.TestRequestDetailView.as_view(), name='detail'),
]

