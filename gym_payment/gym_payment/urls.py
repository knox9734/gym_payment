# gym_payment/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
]