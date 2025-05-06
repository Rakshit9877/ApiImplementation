from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .forms import LoginForm

app_name = 'accounts'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('terms/', views.terms, name='terms'),
    path('face-registration/', views.face_registration, name='face_registration'),
    path('face-login/', views.face_login, name='face_login'),
    path('face-login-auth/', views.face_login_auth, name='face_login_auth'),
    path('dashboard/', views.dashboard, name='dashboard'),
] 