"""
URL configuration for products app.
"""
from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.ProductListView.as_view(), name='list'),
    path('create/', views.ProductCreateView.as_view(), name='create'),
    path('<uuid:pk>/update/', views.ProductUpdateView.as_view(), name='update'),
    path('<uuid:pk>/delete/', views.ProductDeleteView.as_view(), name='delete'),
    path('suppliers/', views.SupplierListView.as_view(), name='supplier_list'),
    path('suppliers/create/', views.SupplierCreateView.as_view(), name='supplier_create'),
    path('suppliers/<uuid:pk>/update/', views.SupplierUpdateView.as_view(), name='supplier_update'),
    path('suppliers/<uuid:pk>/delete/', views.SupplierDeleteView.as_view(), name='supplier_delete'),
    path('groups/', views.ProductGroupListView.as_view(), name='group_list'),
    path('groups/create/', views.ProductGroupCreateView.as_view(), name='group_create'),
    path('groups/<uuid:pk>/update/', views.ProductGroupUpdateView.as_view(), name='group_update'),
    path('groups/<uuid:pk>/delete/', views.ProductGroupDeleteView.as_view(), name='group_delete'),
    path('units/', views.UnitOfMeasureListView.as_view(), name='unit_list'),
    path('units/create/', views.UnitOfMeasureCreateView.as_view(), name='unit_create'),
    path('units/<uuid:pk>/update/', views.UnitOfMeasureUpdateView.as_view(), name='unit_update'),
    path('units/<uuid:pk>/delete/', views.UnitOfMeasureDeleteView.as_view(), name='unit_delete'),
]

