"""
Core base models for the QMS application.
"""
import uuid
from django.db import models
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from django.db.models import Model


class TimestampedModel(models.Model):
    """
    Abstract base model with timestamps only (no id field).
    Used for models that already have their own primary key.
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    
    class Meta:
        abstract = True


class BaseModel(models.Model):
    """
    Abstract base model with UUID primary key, timestamps, and soft delete.
    
    All models in the application should inherit from this base class.
    Note: Do not use for User model as it extends AbstractUser which has its own id.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name='ID'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Created At'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Updated At'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Is Active',
        help_text='Designates whether this record is active. Unselect this instead of deleting.'
    )
    
    class Meta:
        abstract = True
        ordering = ['-created_at']
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.id})"
    
    def soft_delete(self) -> None:
        """
        Soft delete the record by setting is_active to False.
        """
        self.is_active = False
        self.save(update_fields=['is_active', 'updated_at'])
