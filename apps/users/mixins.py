"""
Role-based access control mixins for class-based views.
"""
from typing import List, Literal
from django.contrib.auth.mixins import LoginRequiredMixin, AccessMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.http import HttpRequest

from .permissions import has_admin_access, has_controller_access


class RoleRequiredMixin(LoginRequiredMixin, AccessMixin):
    """
    Mixin to require specific role(s) for a view.
    
    Usage:
        class MyView(RoleRequiredMixin, View):
            required_roles = ['ADMIN', 'CONTROLLER']
    """
    required_roles: List[Literal['ADMIN', 'CONTROLLER']] = []
    
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if self.required_roles and request.user.role not in self.required_roles:
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class AdminRequiredMixin(LoginRequiredMixin, AccessMixin):
    """
    Mixin to require admin role for a view.
    
    Usage:
        class AdminView(AdminRequiredMixin, View):
            ...
    """
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        if not has_admin_access(request.user):
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)


class ControllerRequiredMixin(LoginRequiredMixin, AccessMixin):
    """
    Mixin to require controller role for a view.
    Admins also have access (admins can access everything).
    
    Usage:
        class ControllerView(ControllerRequiredMixin, View):
            ...
    """
    def dispatch(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Allow both controllers and admins (admins have full access)
        if not (has_controller_access(request.user) or has_admin_access(request.user)):
            messages.error(request, 'Controller access required.')
            return redirect('dashboard')
        
        return super().dispatch(request, *args, **kwargs)

