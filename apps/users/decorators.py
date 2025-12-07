"""
Role-based access control decorators for function-based views.
"""
from functools import wraps
from typing import List, Literal
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpRequest, HttpResponse

from .permissions import has_admin_access, has_controller_access


def role_required(roles: List[Literal['ADMIN', 'CONTROLLER']]):
    """
    Decorator to require specific role(s) for a view.
    
    Args:
        roles: List of allowed roles
        
    Usage:
        @role_required(['ADMIN', 'CONTROLLER'])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
            user = request.user
            if user.role not in roles:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def admin_required(view_func):
    """
    Decorator to require admin role for a view.
    
    Usage:
        @admin_required
        def admin_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        if not has_admin_access(request.user):
            messages.error(request, 'Admin access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


def controller_required(view_func):
    """
    Decorator to require controller role for a view.
    Admins also have access (admins can access everything).
    
    Usage:
        @controller_required
        def controller_view(request):
            ...
    """
    @wraps(view_func)
    @login_required
    def wrapper(request: HttpRequest, *args, **kwargs) -> HttpResponse:
        # Allow both controllers and admins (admins have full access)
        if not (has_controller_access(request.user) or has_admin_access(request.user)):
            messages.error(request, 'Controller access required.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper

