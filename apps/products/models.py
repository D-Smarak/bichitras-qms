"""
Product models for the QMS application.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from typing import Literal, Optional

from apps.core.models import BaseModel


class ProductGroup(BaseModel):
    """
    Hierarchical product category/group structure.
    
    Supports parent-child relationships for organizing products.
    """
    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name='Code',
        help_text='Unique code for the product group'
    )
    name = models.CharField(
        max_length=100,
        verbose_name='Name'
    )
    parent_group = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='child_groups',
        verbose_name='Parent Group',
        help_text='Parent category for hierarchical organization'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description'
    )
    
    class Meta:
        verbose_name = 'Product Group'
        verbose_name_plural = 'Product Groups'
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class UnitOfMeasure(BaseModel):
    """
    Unit of measure for products (e.g., kg, litre, pcs).
    """
    UNIT_CHOICES = [
        ('pcs', 'Pieces'),
        ('kg', 'Kilograms'),
        ('g', 'Grams'),
        ('l', 'Liters'),
        ('ml', 'Milliliters'),
        ('m', 'Meters'),
        ('cm', 'Centimeters'),
        ('box', 'Box'),
        ('pack', 'Pack'),
        ('set', 'Set'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Name',
        help_text='Full name of the unit (e.g., Kilograms)'
    )
    symbol = models.CharField(
        max_length=20,
        choices=UNIT_CHOICES,
        verbose_name='Symbol',
        help_text='Unit symbol (e.g., kg)'
    )
    
    class Meta:
        verbose_name = 'Unit of Measure'
        verbose_name_plural = 'Units of Measure'
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.symbol})"


class Supplier(BaseModel):
    """
    Supplier information for raw materials and products.
    """
    STATUS_CHOICES = [
        ('approved', 'Approved'),
        ('pending', 'Pending'),
        ('rejected', 'Rejected'),
        ('blacklisted', 'Blacklisted'),
    ]
    
    RATING_CHOICES = [(i, str(i)) for i in range(1, 6)]
    
    supplier_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Supplier Code',
        help_text='Unique code for the supplier'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name'
    )
    contact_person = models.CharField(
        max_length=100,
        verbose_name='Contact Person'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    phone = models.CharField(
        max_length=20,
        verbose_name='Phone'
    )
    address = models.TextField(
        verbose_name='Address'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='City'
    )
    country = models.CharField(
        max_length=100,
        default='India',
        verbose_name='Country'
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='Rating',
        help_text='Supplier rating from 1 to 5'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Status'
    )
    
    class Meta:
        verbose_name = 'Supplier'
        verbose_name_plural = 'Suppliers'
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.supplier_code} - {self.name}"


class ProductMaster(BaseModel):
    """
    Master product information with inventory, pricing, and categorization.
    
    Supports different product types: RM (Raw Material), FG (Finished Goods),
    IH (In-House), FF (Finished Feed).
    """
    PRODUCT_TYPE_CHOICES = [
        ('RM', 'Raw Material'),
        ('FG', 'Finished Goods'),
        ('IH', 'In-House'),
        ('FF', 'Finished Feed'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('pending', 'Pending Approval'),
        ('discontinued', 'Discontinued'),
    ]
    
    # Basic Fields
    product_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Product Code',
        help_text='Unique product identifier'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Name'
    )
    generic_name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Generic Name'
    )
    short_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Short Name'
    )
    description = models.TextField(
        verbose_name='Description'
    )
    hs_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='HS Code',
        help_text='Harmonized System code for customs'
    )
    
    # Relations
    category = models.ForeignKey(
        ProductGroup,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='products',
        verbose_name='Category'
    )
    unit = models.ForeignKey(
        UnitOfMeasure,
        on_delete=models.PROTECT,
        related_name='products',
        verbose_name='Unit of Measure'
    )
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_products',
        verbose_name='Created By'
    )
    
    # Inventory Flags
    is_batch_tracked = models.BooleanField(
        default=False,
        verbose_name='Batch Tracked',
        help_text='Whether this product is tracked by batch number'
    )
    is_serial_tracked = models.BooleanField(
        default=False,
        verbose_name='Serial Tracked',
        help_text='Whether this product is tracked by serial number'
    )
    
    # Pricing
    buy_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Buy Price'
    )
    mrp = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='MRP',
        help_text='Maximum Retail Price'
    )
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Cost Price'
    )
    
    # Stock Levels
    quantity = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name='Current Quantity',
        help_text='Current stock quantity'
    )
    min_quantity = models.IntegerField(
        default=10,
        validators=[MinValueValidator(0)],
        verbose_name='Minimum Quantity',
        help_text='Minimum stock level before reorder'
    )
    max_quantity = models.IntegerField(
        default=100,
        validators=[MinValueValidator(0)],
        verbose_name='Maximum Quantity',
        help_text='Maximum stock level'
    )
    
    # Category & Status
    product_type_category = models.CharField(
        max_length=2,
        choices=PRODUCT_TYPE_CHOICES,
        verbose_name='Product Type',
        help_text='Product category type (RM, FG, IH, FF)'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Status'
    )
    
    class Meta:
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['product_code']
        indexes = [
            models.Index(fields=['product_code']),
            models.Index(fields=['product_type_category']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self) -> str:
        return f"{self.product_code} - {self.name}"
    
    @property
    def stock_status(self) -> Literal['low', 'normal', 'high']:
        """
        Calculate stock status based on current quantity.
        
        Returns:
            str: 'low', 'normal', or 'high'
        """
        if self.quantity <= self.min_quantity:
            return 'low'
        elif self.quantity >= self.max_quantity:
            return 'high'
        else:
            return 'normal'
    
    @property
    def total_value(self) -> Decimal:
        """
        Calculate total inventory value (price * quantity).
        
        Returns:
            Decimal: Total value of current stock
        """
        try:
            price = self.cost_price or self.buy_price or Decimal('0.00')
            return price * Decimal(self.quantity)
        except (ValueError, TypeError):
            return Decimal('0.00')
