"""
Filters for analytics views.
"""
import django_filters
from apps.testing.models import TestRequest, TestResult
from apps.products.models import ProductMaster, Supplier
from apps.quality.models import TestParameter


class TestRequestFilter(django_filters.FilterSet):
    """
    Filter for test requests.
    """
    product = django_filters.ModelChoiceFilter(
        queryset=ProductMaster.objects.filter(is_active=True),
        label='Product'
    )
    supplier = django_filters.ModelChoiceFilter(
        queryset=Supplier.objects.filter(is_active=True),
        label='Supplier'
    )
    status = django_filters.ChoiceFilter(
        choices=TestRequest.STATUS_CHOICES,
        label='Status'
    )
    sample_date_from = django_filters.DateFilter(
        field_name='sample_date',
        lookup_expr='gte',
        label='Sample Date From'
    )
    sample_date_to = django_filters.DateFilter(
        field_name='sample_date',
        lookup_expr='lte',
        label='Sample Date To'
    )
    
    class Meta:
        model = TestRequest
        fields = ['product', 'supplier', 'status']


class TestResultFilter(django_filters.FilterSet):
    """
    Filter for test results.
    """
    parameter = django_filters.ModelChoiceFilter(
        queryset=TestParameter.objects.filter(is_active=True),
        label='Parameter'
    )
    pass_fail_status = django_filters.BooleanFilter(
        label='Pass/Fail Status'
    )
    test_request__product = django_filters.ModelChoiceFilter(
        queryset=ProductMaster.objects.filter(is_active=True),
        label='Product'
    )
    
    class Meta:
        model = TestResult
        fields = ['parameter', 'pass_fail_status']

