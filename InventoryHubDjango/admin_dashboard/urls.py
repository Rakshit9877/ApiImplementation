from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('inventory-logs/', views.admin_inventory_logs, name='inventory_logs'),
    path('users/', views.user_management, name='user_management'),
    path('user-management/', views.user_management, name='user_management'),
    path('user-management/add/', views.add_user, name='add_user'),
    path('user-management/edit/<int:user_id>/', views.edit_user, name='edit_user'),
]