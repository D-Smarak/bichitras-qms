"""
Permission constants and helper functions for role-based access control.
"""
from typing import Literal
from django.contrib.auth import get_user_model

User = get_user_model()

# Permission constants
PERMISSION_ADMIN_ACCESS = 'admin_access'
PERMISSION_CONTROLLER_ACCESS = 'controller_access'
PERMISSION_PRODUCT_MANAGE = 'product_manage'
PERMISSION_SUPPLIER_MANAGE = 'supplier_manage'
PERMISSION_SPECIFICATION_MANAGE = 'specification_manage'
PERMISSION_TEST_CREATE = 'test_create'
PERMISSION_TEST_VIEW = 'test_view'
PERMISSION_ANALYTICS_VIEW = 'analytics_view'


def has_admin_access(user: User) -> bool:
    """
    Check if user has admin access.
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user is admin, False otherwise
    """
    return user.is_authenticated and user.is_admin()


def has_controller_access(user: User) -> bool:
    """
    Check if user has controller access.
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user is controller, False otherwise
    """
    return user.is_authenticated and user.is_controller()


def can_manage_products(user: User) -> bool:
    """
    Check if user can manage products (admin only).
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user can manage products, False otherwise
    """
    return has_admin_access(user)


def can_manage_suppliers(user: User) -> bool:
    """
    Check if user can manage suppliers (admin only).
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user can manage suppliers, False otherwise
    """
    return has_admin_access(user)


def can_manage_specifications(user: User) -> bool:
    """
    Check if user can manage specifications (admin only).
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user can manage specifications, False otherwise
    """
    return has_admin_access(user)


def can_create_tests(user: User) -> bool:
    """
    Check if user can create tests (controller only).
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user can create tests, False otherwise
    """
    return has_controller_access(user)


def can_view_analytics(user: User) -> bool:
    """
    Check if user can view analytics (admin only).
    
    Args:
        user: User instance to check
        
    Returns:
        bool: True if user can view analytics, False otherwise
    """
    return has_admin_access(user)


def has_permission(user: User, permission: str) -> bool:
    """
    Generic permission checker.
    
    Args:
        user: User instance to check
        permission: Permission constant to check
        
    Returns:
        bool: True if user has the permission, False otherwise
    """
    permission_map = {
        PERMISSION_ADMIN_ACCESS: has_admin_access,
        PERMISSION_CONTROLLER_ACCESS: has_controller_access,
        PERMISSION_PRODUCT_MANAGE: can_manage_products,
        PERMISSION_SUPPLIER_MANAGE: can_manage_suppliers,
        PERMISSION_SPECIFICATION_MANAGE: can_manage_specifications,
        PERMISSION_TEST_CREATE: can_create_tests,
        PERMISSION_ANALYTICS_VIEW: can_view_analytics,
    }
    
    checker = permission_map.get(permission)
    if checker:
        return checker(user)
    return False

