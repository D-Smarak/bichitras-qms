"""
Quality configuration models for the QMS application.
"""
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from typing import Literal, Optional

from apps.core.models import BaseModel


class TestMethod(BaseModel):
    """
    Standard test methods used for quality testing (e.g., ISO 6579, AOAC 920.87, ASTM D123).
    
    Test methods define the standardized procedures for testing parameters.
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name='Method Code',
        help_text='Short code for the test method (e.g., ISO6579, AOAC920.87)'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Method Name',
        help_text='Full name of the test method'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Description',
        help_text='Detailed description of the test method'
    )
    standard_organization = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Standard Organization',
        help_text='Organization that published the standard (e.g., ISO, AOAC, ASTM)'
    )
    
    class Meta:
        verbose_name = 'Test Method'
        verbose_name_plural = 'Test Methods'
        ordering = ['name']
    
    def __str__(self) -> str:
        if self.standard_organization:
            return f"{self.code} - {self.name} ({self.standard_organization})"
        return f"{self.code} - {self.name}"


class TestParameter(BaseModel):
    """
    Master list of all test parameters (e.g., Moisture, Ash%, Aflatoxin).
    
    Defines what can be tested for products.
    """
    DATA_TYPE_CHOICES = [
        ('Numeric', 'Numeric'),
        ('Text', 'Text'),
        ('Boolean', 'Boolean'),
    ]
    
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Parameter Name',
        help_text='Name of the test parameter (e.g., Moisture, Ash%, Aflatoxin)'
    )
    data_type = models.CharField(
        max_length=20,
        choices=DATA_TYPE_CHOICES,
        default='Numeric',
        verbose_name='Data Type',
        help_text='Type of data this parameter accepts'
    )
    
    class Meta:
        verbose_name = 'Test Parameter'
        verbose_name_plural = 'Test Parameters'
        ordering = ['name']
    
    def __str__(self) -> str:
        return f"{self.name} ({self.get_data_type_display()})"


class ProductSpecification(BaseModel):
    """
    Links a Product to TestParameters with acceptable limits and specifications.
    
    Defines quality standards for products (e.g., Corn must have Moisture between 10% and 12%).
    """
    product = models.ForeignKey(
        'products.ProductMaster',
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name='Product'
    )
    parameter = models.ForeignKey(
        TestParameter,
        on_delete=models.CASCADE,
        related_name='specifications',
        verbose_name='Test Parameter'
    )
    
    # Target and limit values
    target_value = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Target Value',
        help_text='Target or expected value for this parameter'
    )
    
    # Numeric limits (for Numeric data type)
    min_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Minimum Value',
        help_text='Minimum acceptable value (for numeric parameters)'
    )
    max_value = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        verbose_name='Maximum Value',
        help_text='Maximum acceptable value (for numeric parameters)'
    )
    
    # Text/Boolean limits (for Text/Boolean data types)
    min_limit = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Minimum Limit',
        help_text='Minimum limit (for text parameters)'
    )
    max_limit = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Maximum Limit',
        help_text='Maximum limit (for text parameters)'
    )
    
    # Standard value for text/boolean
    standard_text_value = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Standard Text Value',
        help_text='Standard value for text or boolean parameters'
    )
    
    # Additional information
    unit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Unit',
        help_text='Unit of measurement (e.g., %, ppm, mg/kg)'
    )
    test_method = models.ForeignKey(
        TestMethod,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='specifications',
        verbose_name='Test Method',
        help_text='Standard method used to test this parameter'
    )
    is_critical = models.BooleanField(
        default=False,
        verbose_name='Critical Parameter',
        help_text='Whether this is a critical parameter that must pass'
    )
    notes = models.TextField(
        blank=True,
        verbose_name='Notes',
        help_text='Additional notes or instructions'
    )
    
    # Audit
    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_specifications',
        verbose_name='Created By'
    )
    
    class Meta:
        verbose_name = 'Product Specification'
        verbose_name_plural = 'Product Specifications'
        ordering = ['product', 'parameter']
        unique_together = [['product', 'parameter']]
    
    def __str__(self) -> str:
        return f"{self.product.product_code} - {self.parameter.name}"
    
    def validate_value(self, actual_value: str) -> tuple[bool, Optional[str]]:
        """
        Validate an actual test value against this specification.
        
        Args:
            actual_value: The actual test result value (as string)
            
        Returns:
            tuple: (is_valid, error_message)
                - is_valid: True if value passes, False otherwise
                - error_message: Error message if validation fails, None otherwise
        """
        if self.parameter.data_type == 'Numeric':
            try:
                value = Decimal(str(actual_value))
                if self.min_value is not None and value < self.min_value:
                    return False, f"Value {value} is below minimum {self.min_value}"
                if self.max_value is not None and value > self.max_value:
                    return False, f"Value {value} is above maximum {self.max_value}"
                return True, None
            except (ValueError, TypeError):
                return False, f"Invalid numeric value: {actual_value}"
        
        elif self.parameter.data_type == 'Text':
            if self.standard_text_value:
                if actual_value.strip().lower() != self.standard_text_value.strip().lower():
                    return False, f"Value '{actual_value}' does not match standard '{self.standard_text_value}'"
            return True, None
        
        elif self.parameter.data_type == 'Boolean':
            # For boolean, check if value matches standard_text_value
            if self.standard_text_value:
                expected = self.standard_text_value.strip().lower() in ['true', 'yes', '1', 'pass']
                actual = actual_value.strip().lower() in ['true', 'yes', '1', 'pass']
                if expected != actual:
                    return False, f"Boolean value mismatch"
            return True, None
        
        return True, None
