"""
Testing pipeline models for the QMS application.
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from typing import Literal, Optional

from apps.core.models import BaseModel


class TestRequest(BaseModel):
    """
    Test request representing a sample that needs to be tested.
    
    Tracks the testing pipeline through multiple steps (1-4).
    """
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('In-Progress', 'In-Progress'),
        ('Submitted for Review', 'Submitted for Review'),
        ('Completed', 'Completed'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    
    batch_number = models.CharField(
        max_length=100,
        verbose_name='Batch Number',
        help_text='Batch or lot number of the sample'
    )
    supplier = models.ForeignKey(
        'products.Supplier',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_requests',
        verbose_name='Supplier'
    )
    product = models.ForeignKey(
        'products.ProductMaster',
        on_delete=models.PROTECT,
        related_name='test_requests',
        verbose_name='Product'
    )
    controller_user = models.ForeignKey(
        'users.User',
        on_delete=models.PROTECT,
        related_name='test_requests',
        verbose_name='Controller',
        help_text='User responsible for this test'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Pending',
        verbose_name='Status'
    )
    sample_date = models.DateField(
        verbose_name='Sample Date',
        help_text='Date when the sample was received'
    )
    remarks = models.TextField(
        blank=True,
        verbose_name='Remarks',
        help_text='Additional notes or comments'
    )
    current_step = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name='Current Step',
        help_text='Current step in the testing pipeline (1-4)'
    )
    
    class Meta:
        verbose_name = 'Test Request'
        verbose_name_plural = 'Test Requests'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['batch_number']),
            models.Index(fields=['status']),
            models.Index(fields=['sample_date']),
        ]
    
    def __str__(self) -> str:
        return f"Test Request {self.batch_number} - {self.product.name}"
    
    def get_progress_percentage(self) -> int:
        """
        Calculate progress percentage based on current step and status.
        
        Business Logic:
        - Steps 1-3: 25%, 50%, 75% respectively
        - Step 4 + "Submitted for Review": 75%
        - Step 4 + "Approved": 100%
        - Step 4 + "Completed": 100% (legacy)
        
        Returns:
            int: Progress percentage (0-100)
        """
        if self.status == 'Approved' or (self.status == 'Completed' and self.current_step == 4):
            return 100
        elif self.status == 'Submitted for Review':
            return 75
        elif self.current_step == 4:
            return 100  # Step 4 completed but not yet submitted/approved
        else:
            return int((self.current_step / 4) * 100)
    
    def can_proceed_to_next_step(self) -> bool:
        """
        Check if the test request can proceed to the next step.
        
        Returns:
            bool: True if can proceed, False otherwise
        """
        if self.status == 'Rejected':
            return False
        if self.current_step >= 4:
            return False
        return True
    
    def advance_step(self) -> bool:
        """
        Advance to the next step in the pipeline.
        
        Returns:
            bool: True if advanced, False if already at final step
        """
        if self.can_proceed_to_next_step():
            self.current_step += 1
            if self.current_step == 4:
                self.status = 'Completed'
            else:
                self.status = 'In-Progress'
            self.save(update_fields=['current_step', 'status', 'updated_at'])
            return True
        return False


class TestResult(BaseModel):
    """
    Individual test result for a specific parameter within a test request.
    
    Automatically calculates pass/fail status based on product specifications.
    """
    test_request = models.ForeignKey(
        TestRequest,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Test Request'
    )
    parameter = models.ForeignKey(
        'quality.TestParameter',
        on_delete=models.PROTECT,
        related_name='test_results',
        verbose_name='Test Parameter'
    )
    actual_value = models.CharField(
        max_length=200,
        verbose_name='Actual Value',
        help_text='Actual test result value (can be numeric, text, or boolean)'
    )
    pass_fail_status = models.BooleanField(
        null=True,
        blank=True,
        verbose_name='Pass/Fail Status',
        help_text='True if test passed, False if failed, None if not yet calculated'
    )
    tested_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='test_results',
        verbose_name='Tested By'
    )
    tested_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Tested At'
    )
    
    class Meta:
        verbose_name = 'Test Result'
        verbose_name_plural = 'Test Results'
        ordering = ['test_request', 'parameter']
        unique_together = [['test_request', 'parameter']]
    
    def __str__(self) -> str:
        status = "Pass" if self.pass_fail_status else "Fail" if self.pass_fail_status is False else "Pending"
        return f"{self.test_request.batch_number} - {self.parameter.name}: {self.actual_value} ({status})"
    
    def calculate_pass_fail(self) -> bool:
        """
        Calculate pass/fail status based on product specification.
        
        This method:
        1. Finds the ProductSpecification for this test_request's product and parameter
        2. Validates the actual_value against the specification
        3. Updates pass_fail_status field
        4. Saves the model
        
        Returns:
            bool: True if test passed, False if failed
        """
        try:
            # Get the product specification for this product and parameter
            specification = self.test_request.product.specifications.filter(
                parameter=self.parameter,
                is_active=True
            ).first()
            
            if not specification:
                # No specification found - cannot determine pass/fail
                self.pass_fail_status = None
                self.save(update_fields=['pass_fail_status', 'updated_at'])
                return False
            
            # Validate the actual value against the specification
            is_valid, error_message = specification.validate_value(self.actual_value)
            
            self.pass_fail_status = is_valid
            self.save(update_fields=['pass_fail_status', 'updated_at'])
            
            return is_valid
            
        except Exception as e:
            # Error in calculation - mark as None
            self.pass_fail_status = None
            self.save(update_fields=['pass_fail_status', 'updated_at'])
            return False
    
    def save(self, *args, **kwargs):
        """
        Override save to automatically calculate pass/fail if not set.
        """
        # Only calculate if pass_fail_status is None and we have actual_value
        if self.pass_fail_status is None and self.actual_value:
            # Calculate will be called, but we need to save first to get the test_request
            super().save(*args, **kwargs)
            if self.test_request_id and self.parameter_id:
                self.calculate_pass_fail()
        else:
            super().save(*args, **kwargs)
