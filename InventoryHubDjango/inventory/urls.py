from django.urls import path
from . import views

app_name = 'inventory'

urlpatterns = [
    path('', views.inventory_home, name='inventory_home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('add-item/', views.add_item, name='add_item'),
    path('items/', views.item_list, name='item_list'),
    path('items/delete/<int:item_id>/', views.delete_item, name='delete_item'),
    path('items/update/<int:item_id>/', views.update_item, name='update_item'),
    path('groups/', views.group_list, name='group_list'),
    path('groups/add/', views.add_group, name='add_group'),
    path('groups/edit/<int:group_id>/', views.edit_group, name='edit_group'),
    path('groups/delete/<int:group_id>/', views.delete_group, name='delete_group'),
    path('api/group/<int:group_id>/attributes/', views.group_attributes_api, name='group_attributes_api'),
    path('about/', views.about, name='about'),
] 