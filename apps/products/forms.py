"""
Forms for product management.
"""
from django import forms
from .models import ProductMaster, Supplier, ProductGroup, UnitOfMeasure


class ProductForm(forms.ModelForm):
    """
    Form for product creation and update.
    """
    class Meta:
        model = ProductMaster
        fields = [
            'product_code', 'name', 'generic_name', 'short_name', 'description',
            'hs_code', 'category', 'unit', 'is_batch_tracked', 'is_serial_tracked',
            'buy_price', 'mrp', 'cost_price', 'quantity', 'min_quantity', 'max_quantity',
            'product_type_category', 'status'
        ]
        widgets = {
            'product_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'generic_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'short_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
            'hs_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'unit': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'is_batch_tracked': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'is_serial_tracked': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'buy_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'step': '0.01'}),
            'mrp': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'step': '0.01'}),
            'cost_price': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded', 'step': '0.01'}),
            'quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'max_quantity': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'product_type_category': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = ProductGroup.objects.filter(is_active=True)
        self.fields['unit'].queryset = UnitOfMeasure.objects.filter(is_active=True)


class SupplierForm(forms.ModelForm):
    """
    Form for supplier creation and update.
    """
    class Meta:
        model = Supplier
        fields = [
            'supplier_code', 'name', 'contact_person', 'email', 'phone',
            'address', 'city', 'country', 'rating', 'status'
        ]
        widgets = {
            'supplier_code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'contact_person': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'address': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'country': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'rating': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'status': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }


class ProductGroupForm(forms.ModelForm):
    """
    Form for product group (category) creation and update.
    """
    class Meta:
        model = ProductGroup
        fields = ['code', 'name', 'parent_group', 'description']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'parent_group': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border rounded', 'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Exclude self from parent_group choices to prevent circular references
        if self.instance and self.instance.pk:
            self.fields['parent_group'].queryset = ProductGroup.objects.filter(
                is_active=True
            ).exclude(pk=self.instance.pk)
        else:
            self.fields['parent_group'].queryset = ProductGroup.objects.filter(is_active=True)


class UnitOfMeasureForm(forms.ModelForm):
    """
    Form for unit of measure creation and update.
    """
    class Meta:
        model = UnitOfMeasure
        fields = ['name', 'symbol']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'symbol': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        }

