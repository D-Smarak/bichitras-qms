"""
User authentication and management views.
"""
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.contrib import messages
from django.urls import reverse_lazy

from apps.users.mixins import AdminRequiredMixin
from .models import User
from .forms import LoginForm, UserForm, UserCreateForm


class CustomLoginView(LoginView):
    """
    Custom login view using Jinja2 templates.
    """
    template_name = 'users/login.html'
    form_class = LoginForm
    redirect_authenticated_user = True


def logout_view(request):
    """
    Logout view.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('users:login')


class UserListView(AdminRequiredMixin, ListView):
    """
    List view for users (Admin only).
    """
    model = User
    template_name = 'admin/users/list.html'
    context_object_name = 'users'
    paginate_by = 20
    
    def get_queryset(self):
        return User.objects.all().order_by('-date_joined')


class UserCreateView(AdminRequiredMixin, CreateView):
    """
    Create view for users (Admin only).
    """
    model = User
    form_class = UserCreateForm
    template_name = 'admin/users/form.html'
    success_url = reverse_lazy('users:list')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.set_password(form.cleaned_data['password'])
        user.save()
        messages.success(self.request, f'User {user.username} created successfully.')
        return super().form_valid(form)


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """
    Update view for users (Admin only).
    """
    model = User
    form_class = UserForm
    template_name = 'admin/users/form.html'
    success_url = reverse_lazy('users:list')
    
    def form_valid(self, form):
        # Handle password change if provided
        if 'password' in form.cleaned_data and form.cleaned_data['password']:
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
        else:
            form.save()
        messages.success(self.request, f'User {form.instance.username} updated successfully.')
        return redirect(self.success_url)


class UserDeleteView(AdminRequiredMixin, DeleteView):
    """
    Delete view for users (soft delete, Admin only).
    """
    model = User
    template_name = 'admin/users/confirm_delete.html'
    success_url = reverse_lazy('users:list')
    
    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Prevent deleting yourself
        if self.object == request.user:
            messages.error(request, 'You cannot delete your own account.')
            return redirect(self.success_url)
        self.object.soft_delete()
        messages.success(request, f'User {self.object.username} deleted successfully.')
        return redirect(self.success_url)
