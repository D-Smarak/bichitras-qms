"""
URL configuration for quality app.
"""
from django.urls import path
from . import views

app_name = 'quality'

urlpatterns = [
    path('specifications/', views.SpecificationListView.as_view(), name='specification_list'),
    path('specifications/create/', views.SpecificationCreateView.as_view(), name='specification_create'),
    path('specifications/<uuid:pk>/update/', views.SpecificationUpdateView.as_view(), name='specification_update'),
    path('specifications/<uuid:pk>/delete/', views.SpecificationDeleteView.as_view(), name='specification_delete'),
    path('parameters/', views.TestParameterListView.as_view(), name='parameter_list'),
    path('parameters/create/', views.TestParameterCreateView.as_view(), name='parameter_create'),
    path('parameters/<uuid:pk>/update/', views.TestParameterUpdateView.as_view(), name='parameter_update'),
    path('parameters/<uuid:pk>/delete/', views.TestParameterDeleteView.as_view(), name='parameter_delete'),
    path('methods/', views.TestMethodListView.as_view(), name='method_list'),
    path('methods/create/', views.TestMethodCreateView.as_view(), name='method_create'),
    path('methods/<uuid:pk>/update/', views.TestMethodUpdateView.as_view(), name='method_update'),
    path('methods/<uuid:pk>/delete/', views.TestMethodDeleteView.as_view(), name='method_delete'),
]

