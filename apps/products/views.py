"""
Product management views (Admin only).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from apps.users.mixins import AdminRequiredMixin
from .models import ProductMaster, Supplier, ProductGroup, UnitOfMeasure
from .forms import ProductForm, SupplierForm, ProductGroupForm, UnitOfMeasureForm


class ProductListView(AdminRequiredMixin, ListView):
    """
    List view for products.
    """
    model = ProductMaster
    template_name = 'admin/products/list.html'
    context_object_name = 'products'
    paginate_by = 20
    
    def get_queryset(self):
        return ProductMaster.objects.filter(is_active=True).select_related('category', 'unit').order_by('-created_at')


class ProductCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for products.
    """
    model = ProductMaster
    form_class = ProductForm
    template_name = 'admin/products/form.html'
    success_url = reverse_lazy('products:list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Product created successfully.')
        return super().form_valid(form)


class ProductUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for products.
    """
    model = ProductMaster
    form_class = ProductForm
    template_name = 'admin/products/form.html'
    success_url = reverse_lazy('products:list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product updated successfully.')
        return super().form_valid(form)


class ProductDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for products (soft delete).
    """
    model = ProductMaster
    template_name = 'admin/products/confirm_delete.html'
    success_url = reverse_lazy('products:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Product deleted successfully.')
        return redirect(self.success_url)


class SupplierListView(AdminRequiredMixin, ListView):
    """
    List view for suppliers.
    """
    model = Supplier
    template_name = 'admin/suppliers/list.html'
    context_object_name = 'suppliers'
    paginate_by = 20
    
    def get_queryset(self):
        return Supplier.objects.filter(is_active=True).order_by('-created_at')


class SupplierCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for suppliers.
    """
    model = Supplier
    form_class = SupplierForm
    template_name = 'admin/suppliers/form.html'
    success_url = reverse_lazy('products:supplier_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Supplier created successfully.')
        return super().form_valid(form)


class SupplierUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for suppliers.
    """
    model = Supplier
    form_class = SupplierForm
    template_name = 'admin/suppliers/form.html'
    success_url = reverse_lazy('products:supplier_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Supplier updated successfully.')
        return super().form_valid(form)


class SupplierDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for suppliers (soft delete).
    """
    model = Supplier
    template_name = 'admin/suppliers/confirm_delete.html'
    success_url = reverse_lazy('products:supplier_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Supplier deleted successfully.')
        return redirect(self.success_url)


class ProductGroupListView(AdminRequiredMixin, ListView):
    """
    List view for product groups (categories).
    """
    model = ProductGroup
    template_name = 'admin/products/group_list.html'
    context_object_name = 'groups'
    paginate_by = 20
    
    def get_queryset(self):
        return ProductGroup.objects.filter(is_active=True).order_by('name')


class ProductGroupCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for product groups.
    """
    model = ProductGroup
    form_class = ProductGroupForm
    template_name = 'admin/products/group_form.html'
    success_url = reverse_lazy('products:group_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product group created successfully.')
        return super().form_valid(form)


class ProductGroupUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for product groups.
    """
    model = ProductGroup
    form_class = ProductGroupForm
    template_name = 'admin/products/group_form.html'
    success_url = reverse_lazy('products:group_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Product group updated successfully.')
        return super().form_valid(form)


class ProductGroupDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for product groups (soft delete).
    """
    model = ProductGroup
    template_name = 'admin/products/group_confirm_delete.html'
    success_url = reverse_lazy('products:group_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Product group deleted successfully.')
        return redirect(self.success_url)


class UnitOfMeasureListView(AdminRequiredMixin, ListView):
    """
    List view for units of measure.
    """
    model = UnitOfMeasure
    template_name = 'admin/products/unit_list.html'
    context_object_name = 'units'
    paginate_by = 20
    
    def get_queryset(self):
        return UnitOfMeasure.objects.filter(is_active=True).order_by('name')


class UnitOfMeasureCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for units of measure.
    """
    model = UnitOfMeasure
    form_class = UnitOfMeasureForm
    template_name = 'admin/products/unit_form.html'
    success_url = reverse_lazy('products:unit_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Unit of measure created successfully.')
        return super().form_valid(form)


class UnitOfMeasureUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for units of measure.
    """
    model = UnitOfMeasure
    form_class = UnitOfMeasureForm
    template_name = 'admin/products/unit_form.html'
    success_url = reverse_lazy('products:unit_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Unit of measure updated successfully.')
        return super().form_valid(form)


class UnitOfMeasureDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for units of measure (soft delete).
    """
    model = UnitOfMeasure
    template_name = 'admin/products/unit_confirm_delete.html'
    success_url = reverse_lazy('products:unit_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Unit of measure deleted successfully.')
        return redirect(self.success_url)
