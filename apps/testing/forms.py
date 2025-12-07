"""
Forms for testing pipeline.
"""
from django import forms
from .models import TestRequest, TestResult
from apps.products.models import ProductMaster, Supplier
from apps.quality.models import TestParameter, ProductSpecification


class TestRequestForm(forms.ModelForm):
    """
    Form for Step 1: Sample Registration.
    """
    class Meta:
        model = TestRequest
        fields = ['batch_number', 'supplier', 'product', 'sample_date', 'remarks']
        widgets = {
            'batch_number': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'supplier': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'product': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'sample_date': forms.DateInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'type': 'date'}),
            'remarks': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['supplier'].queryset = Supplier.objects.filter(is_active=True, status='approved')
        self.fields['product'].queryset = ProductMaster.objects.filter(is_active=True)


class TestParameterSelectionForm(forms.Form):
    """
    Form for Step 2: Parameter Selection.
    """
    parameters = forms.ModelMultipleChoiceField(
        queryset=TestParameter.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Select Test Parameters'
    )
    
    def __init__(self, *args, **kwargs):
        test_request = kwargs.pop('test_request', None)
        super().__init__(*args, **kwargs)
        if test_request:
            # Get available specifications for this product
            spec_params = ProductSpecification.objects.filter(
                product=test_request.product,
                is_active=True
            ).values_list('parameter_id', flat=True)
            self.fields['parameters'].queryset = TestParameter.objects.filter(
                id__in=spec_params,
                is_active=True
            )


class TestResultForm(forms.Form):
    """
    Dynamic form for Step 3: Results Entry.
    """
    def __init__(self, *args, **kwargs):
        parameters = kwargs.pop('parameters', [])
        super().__init__(*args, **kwargs)
        
        for param in parameters:
            if param.data_type == 'Numeric':
                self.fields[f'value_{param.id}'] = forms.DecimalField(
                    label=param.name,
                    required=True,
                    widget=forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'step': '0.01'})
                )
            elif param.data_type == 'Boolean':
                self.fields[f'value_{param.id}'] = forms.ChoiceField(
                    label=param.name,
                    choices=[('True', 'Yes'), ('False', 'No')],
                    widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'})
                )
            else:
                self.fields[f'value_{param.id}'] = forms.CharField(
                    label=param.name,
                    required=True,
                    widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'})
                )


class TestReviewForm(forms.Form):
    """
    Form for Step 4: Review & Submit.
    """
    ACTION_CHOICES = [
        ('submit', 'Submit for Review'),
        ('approve', 'Approve'),
        ('reject', 'Reject'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        label='Action'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
        required=False,
        label='Additional Notes'
    )

