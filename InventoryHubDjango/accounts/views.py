from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, LoginForm

def login_view(request):
    if request.user.is_authenticated:
        messages.info(request, "You are already logged in!")
        return redirect('index')
    
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Update last login
            if hasattr(user, 'profile'):
                user.profile.last_login = timezone.now()
                user.profile.save()
            
            messages.success(request, f"Welcome back, {user.username}!")
            return redirect('index')  # Changed from 'inventory:dashboard' to 'index'
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Account created successfully! Please login to continue.")
            return redirect('accounts:login')  # Changed: don't login automatically, redirect to login page
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/signup.html', {'form': form})

@login_required
def logout_view(request):
    messages.success(request, f"Goodbye, {request.user.username}! You have been logged out.")
    logout(request)
    return redirect('/')

@login_required
def profile(request):
    messages.info(request, "Viewing your profile information.")
    return render(request, 'accounts/profile.html')

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Your password has been updated successfully!')
            return redirect('accounts:profile')
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})

def terms(request):
    return render(request, 'accounts/terms.html')
