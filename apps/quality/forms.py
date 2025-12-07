"""
Forms for quality specification management.
"""
from django import forms
from .models import ProductSpecification, TestParameter, TestMethod
from apps.products.models import ProductMaster


class ProductSpecificationForm(forms.ModelForm):
    """
    Form for product specification creation and update.
    """
    class Meta:
        model = ProductSpecification
        fields = [
            'product', 'parameter', 'target_value', 'min_value', 'max_value',
            'min_limit', 'max_limit', 'standard_text_value', 'unit', 'test_method',
            'is_critical', 'notes'
        ]
        widgets = {
            'product': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'parameter': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'target_value': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'min_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'step': '0.0001'}),
            'max_value': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'step': '0.0001'}),
            'min_limit': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'max_limit': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'standard_text_value': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'unit': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'test_method': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'is_critical': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'notes': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['product'].queryset = ProductMaster.objects.filter(is_active=True)
        self.fields['parameter'].queryset = TestParameter.objects.filter(is_active=True)
        self.fields['test_method'].queryset = TestMethod.objects.filter(is_active=True)


class TestParameterForm(forms.ModelForm):
    """
    Form for test parameter creation and update.
    """
    class Meta:
        model = TestParameter
        fields = ['name', 'data_type']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'data_type': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }


class TestMethodForm(forms.ModelForm):
    """
    Form for test method creation and update.
    """
    class Meta:
        model = TestMethod
        fields = ['code', 'name', 'description', 'standard_organization']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
            'standard_organization': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }

