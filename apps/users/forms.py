"""
Forms for user authentication and management.
"""
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from .models import User


class LoginForm(AuthenticationForm):
    """
    Login form.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        label='Username'
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
        label='Password'
    )


class UserForm(forms.ModelForm):
    """
    Form for user update (Admin only).
    """
    password = forms.CharField(
        required=False,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded',
            'placeholder': 'Leave blank to keep current password'
        }),
        help_text='Leave blank to keep current password. Enter new password to change it.'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'role': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
        }


class UserCreateForm(forms.ModelForm):
    """
    Form for creating new users (Admin only).
    """
    password = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded',
            'placeholder': 'Enter password'
        }),
        help_text='Required. Enter a secure password for the user.'
    )
    password_confirm = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-2 border rounded',
            'placeholder': 'Confirm password'
        }),
        help_text='Enter the same password as above for verification.'
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'first_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'last_name': forms.TextInput(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'role': forms.Select(attrs={'class': 'w-full px-4 py-2 border rounded'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'w-5 h-5', 'checked': True}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'w-5 h-5'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data
