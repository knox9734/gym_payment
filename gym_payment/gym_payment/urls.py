# gym_payment/urls.py
from django.contrib import admin
from django.urls import path, include
from users import views
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('register/', views.register_user, name='register_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/delete/<int:user_id>/', views.delete_user, name='delete_user'),
    path('add_payment/', views.add_payment, name='add_payment'),
    path('payment_list/', views.payment_list, name='payment_list'),
    path('check_payment_status/', views.check_payment_status, name='check_payment_status'),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(next_page='/home'), name='logout'),
    path('home/', views.welcome, name='home'),
    
]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)