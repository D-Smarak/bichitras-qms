"""
User models for the QMS application.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from typing import Literal

from apps.core.models import TimestampedModel


class User(AbstractUser, TimestampedModel):
    """
    Custom User model extending AbstractUser with role-based access control.
    
    Roles:
    - ADMIN: Full access to master data management and analytics
    - CONTROLLER: Access to testing pipeline and result entry
    """
    ROLE_CHOICES = [
        ('ADMIN', 'Admin'),
        ('CONTROLLER', 'Controller'),
    ]
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='CONTROLLER',
        verbose_name='Role',
        help_text='User role determining access permissions'
    )
    
    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
    
    def __str__(self) -> str:
        return f"{self.username} ({self.get_role_display()})"
    
    def is_admin(self) -> bool:
        """
        Check if user has admin role.
        
        Returns:
            bool: True if user is admin, False otherwise
        """
        return self.role == 'ADMIN'
    
    def is_controller(self) -> bool:
        """
        Check if user has controller role.
        
        Returns:
            bool: True if user is controller, False otherwise
        """
        return self.role == 'CONTROLLER'
    
    def has_role(self, role: Literal['ADMIN', 'CONTROLLER']) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role: Role to check ('ADMIN' or 'CONTROLLER')
            
        Returns:
            bool: True if user has the specified role, False otherwise
        """
        return self.role == role
    
    def soft_delete(self) -> None:
        """
        Soft delete the user by setting is_active to False.
        """
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
