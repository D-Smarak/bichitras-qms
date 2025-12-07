"""
Quality specification management views (Admin only).
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy

from apps.users.mixins import AdminRequiredMixin
from .models import ProductSpecification, TestParameter, TestMethod
from .forms import ProductSpecificationForm, TestParameterForm, TestMethodForm


class SpecificationListView(AdminRequiredMixin, ListView):
    """
    List view for product specifications.
    """
    model = ProductSpecification
    template_name = 'admin/specifications/list.html'
    context_object_name = 'specifications'
    paginate_by = 20
    
    def get_queryset(self):
        return ProductSpecification.objects.filter(is_active=True).select_related('product', 'parameter').order_by('-created_at')


class SpecificationCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for product specifications.
    """
    model = ProductSpecification
    form_class = ProductSpecificationForm
    template_name = 'admin/specifications/form.html'
    success_url = reverse_lazy('quality:specification_list')
    
    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, 'Specification created successfully.')
        return super().form_valid(form)


class SpecificationUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for product specifications.
    """
    model = ProductSpecification
    form_class = ProductSpecificationForm
    template_name = 'admin/specifications/form.html'
    success_url = reverse_lazy('quality:specification_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Specification updated successfully.')
        return super().form_valid(form)


class SpecificationDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for product specifications (soft delete).
    """
    model = ProductSpecification
    template_name = 'admin/specifications/confirm_delete.html'
    success_url = reverse_lazy('quality:specification_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Specification deleted successfully.')
        return redirect(self.success_url)


class TestParameterListView(AdminRequiredMixin, ListView):
    """
    List view for test parameters.
    """
    model = TestParameter
    template_name = 'admin/quality/parameter_list.html'
    context_object_name = 'parameters'
    paginate_by = 20
    
    def get_queryset(self):
        return TestParameter.objects.filter(is_active=True).order_by('name')


class TestParameterCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for test parameters.
    """
    model = TestParameter
    form_class = TestParameterForm
    template_name = 'admin/quality/parameter_form.html'
    success_url = reverse_lazy('quality:parameter_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Test parameter created successfully.')
        return super().form_valid(form)


class TestParameterUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for test parameters.
    """
    model = TestParameter
    form_class = TestParameterForm
    template_name = 'admin/quality/parameter_form.html'
    success_url = reverse_lazy('quality:parameter_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Test parameter updated successfully.')
        return super().form_valid(form)


class TestParameterDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for test parameters (soft delete).
    """
    model = TestParameter
    template_name = 'admin/quality/parameter_confirm_delete.html'
    success_url = reverse_lazy('quality:parameter_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Test parameter deleted successfully.')
        return redirect(self.success_url)


class TestMethodListView(AdminRequiredMixin, ListView):
    """
    List view for test methods.
    """
    model = TestMethod
    template_name = 'admin/quality/method_list.html'
    context_object_name = 'methods'
    paginate_by = 20
    
    def get_queryset(self):
        return TestMethod.objects.filter(is_active=True).order_by('name')


class TestMethodCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for test methods.
    """
    model = TestMethod
    form_class = TestMethodForm
    template_name = 'admin/quality/method_form.html'
    success_url = reverse_lazy('quality:method_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Test method created successfully.')
        return super().form_valid(form)


class TestMethodUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for test methods.
    """
    model = TestMethod
    form_class = TestMethodForm
    template_name = 'admin/quality/method_form.html'
    success_url = reverse_lazy('quality:method_list')
    
    def form_valid(self, form):
        messages.success(self.request, 'Test method updated successfully.')
        return super().form_valid(form)


class TestMethodDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for test methods (soft delete).
    """
    model = TestMethod
    template_name = 'admin/quality/method_confirm_delete.html'
    success_url = reverse_lazy('quality:method_list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.soft_delete()
        messages.success(request, 'Test method deleted successfully.')
        return redirect(self.success_url)
