# gym_payment/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add_payment/', views.add_payment, name='add_payment'),
    path('payment_list/', views.payment_list, name='payment_list'),
]