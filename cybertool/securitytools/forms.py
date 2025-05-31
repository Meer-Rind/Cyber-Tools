from django import forms
from .models import ScanResult, PasswordAudit
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User




class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Your password must contain at least 8 characters."
    )
    password2 = forms.CharField(
        label="Password confirmation",
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        help_text="Enter the same password as before, for verification."
    )

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Your passwords don't match.")
        
        return cleaned_data


class PortScanForm(forms.Form):
    target = forms.CharField(label='Target IP/Hostname', max_length=255)
    ports = forms.CharField(label='Ports (comma separated)', max_length=255, required=False)
    scan_type = forms.ChoiceField(choices=[
        ('quick', 'Quick Scan (Top 100 ports)'),
        ('full', 'Full Scan (1-65535)'),
        ('custom', 'Custom Port Range')
    ])

class PasswordStrengthForm(forms.Form):
    password = forms.CharField(label='Password to test', widget=forms.PasswordInput)

class HashGeneratorForm(forms.Form):
    text = forms.CharField(label='Text to hash', widget=forms.Textarea)
    algorithm = forms.ChoiceField(choices=[
        ('md5', 'MD5'),
        ('sha1', 'SHA-1'),
        ('sha256', 'SHA-256'),
        ('sha512', 'SHA-512'),
    ])

class URLScanForm(forms.Form):
    url = forms.URLField(label='URL to scan')