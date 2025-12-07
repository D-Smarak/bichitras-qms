"""
Jinja2 template tags for role-based access control.
"""
from jinja2 import Environment
from typing import Literal

from ..permissions import (
    has_admin_access,
    has_controller_access,
    has_permission,
)


def has_role(user, role: Literal['ADMIN', 'CONTROLLER']) -> bool:
    """
    Jinja2 filter to check if user has a specific role.
    
    Usage in template:
        {{ user|has_role('ADMIN') }}
    """
    if not user or not user.is_authenticated:
        return False
    return user.has_role(role)


def can_access(user, permission: str) -> bool:
    """
    Jinja2 filter to check if user has a specific permission.
    
    Usage in template:
        {{ user|can_access('product_manage') }}
    """
    if not user or not user.is_authenticated:
        return False
    return has_permission(user, permission)


def is_admin(user) -> bool:
    """
    Jinja2 filter to check if user is admin.
    
    Usage in template:
        {{ user|is_admin }}
    """
    if not user or not user.is_authenticated:
        return False
    return has_admin_access(user)


def is_controller(user) -> bool:
    """
    Jinja2 filter to check if user is controller.
    
    Usage in template:
        {{ user|is_controller }}
    """
    if not user or not user.is_authenticated:
        return False
    return has_controller_access(user)


def register_filters(env: Environment) -> None:
    """
    Register all custom filters with Jinja2 environment.
    
    Args:
        env: Jinja2 environment instance
    """
    env.filters.update({
        'has_role': has_role,
        'can_access': can_access,
        'is_admin': is_admin,
        'is_controller': is_controller,
    })

