"""
The URL patterns are mapped to the corresponding view functions
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home,name='home'),
    # Authentication URLs
    path('register/', views.register, name='register'),
    path('login/', views.login_user,name='login_user'),
    path('logout/', views.logout_user, name='logout_user'),
]