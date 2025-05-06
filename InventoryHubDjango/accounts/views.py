from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, update_session_auth_hash, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .forms import CustomUserCreationForm, CustomPasswordChangeForm, LoginForm
import requests
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from django.http import JsonResponse

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
            return redirect('index')
    else:
        form = LoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})

def register(request):
    if request.user.is_authenticated:
        return redirect('index')
        
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                login(request, user)
                # --- Flask user creation ---
                flask_url = 'http://localhost:5001/register'
                flask_data = {
                    'username': user.username,
                    'email': user.email,
                    'password': request.POST.get('password1'),
                    'phone': user.profile.phone if hasattr(user, 'profile') else '',
                    'country': user.profile.country if hasattr(user, 'profile') else '',
                    'state': user.profile.state if hasattr(user, 'profile') else ''
                }
                try:
                    flask_response = requests.post(flask_url, data=flask_data, timeout=5)
                    # Optionally, check flask_response.status_code and log or handle errors
                except Exception as e:
                    print(f"Error creating user in Flask: {e}")
                # --- End Flask user creation ---
                messages.success(request, f"Account created successfully! Please register your face to continue.")
                print("Registration successful, redirecting to face registration page...")
                return redirect('accounts:face_registration')
            except Exception as e:
                print(f"Error during registration: {str(e)}")
                messages.error(request, "An error occurred during registration. Please try again.")
        else:
            print(f"Form validation errors: {form.errors}")
            messages.error(request, "Please correct the errors below.")
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

def face_registration(request):
    if not request.user.is_authenticated:
        return redirect('accounts:login')
    return render(request, 'accounts/face_registration.html')

def face_login(request):
    if request.user.is_authenticated:
        return redirect('index')
    return render(request, 'accounts/face_login.html')

@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

@csrf_exempt
def face_login_auth(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            user = None
            if username:
                try:
                    user = User.objects.get(username=username)
                except User.DoesNotExist:
                    user = None
            if not user and email:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = None
            if user is not None:
                login(request, user)
                return JsonResponse({'success': True})
            else:
                return JsonResponse({'success': False, 'error': 'User not found.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Invalid request method.'})
