from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile
from django.core.validators import MinLengthValidator, RegexValidator

class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'id': 'username'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Password',
        'id': 'password'
    }))
    
    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = 'Username'

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Email',
        'id': 'email'
    }))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'First Name',
        'id': 'first_name'
    }))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Last Name',
        'id': 'last_name'
    }))
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Username',
        'id': 'username'
    }))
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password',
            'id': 'password1'
        }),
        validators=[
            MinLengthValidator(8, message="Password must be at least 8 characters long."),
            RegexValidator(
                regex=r'^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{8,}$',
                message="Password must contain at least one letter, one number, and one special character."
            )
        ]
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm Password',
            'id': 'password2'
        })
    )
    phone = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Phone',
        'id': 'phone'
    }))
    country = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Country',
        'id': 'country'
    }))
    state = forms.CharField(required=False, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'State',
        'id': 'state'
    }))
    
    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password1", "password2"]
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            user_profile = UserProfile.objects.create(
                user=user,
                phone=self.cleaned_data.get('phone', ''),
                country=self.cleaned_data.get('country', ''),
                state=self.cleaned_data.get('state', '')
            )
        return user

class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Current Password',
        'id': 'old_password'
    }))
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'New Password',
        'id': 'new_password1'
    }))
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Confirm New Password',
        'id': 'new_password2'
    }))
    
    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2'] 