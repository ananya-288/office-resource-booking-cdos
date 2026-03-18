"""
The URL patterns are mapped to the corresponding view functions
"""
from django.urls import path
from . import views

urlpatterns = [
    # Home page
    path('', views.home,name='home'),
    # Authentication URLs
    path('register/',views.register,name='register'),
    path('login/',views.login_user,name='login_user'),
    path('logout/',views.logout_user,name='logout_user'),
    # Resource URLs
    path('resources/',views.list_resources, name='list_resources'),
    path('resources/<int:pk>/',views.resource_detail,name='resource_detail'),
    path('resources/create/', views.resource_create,name='resource_create'),
    path('resources/<int:pk>/edit/',views.resource_edit, name='resource_edit'),
    path('resources/<int:pk>/delete/', views.resource_delete,name='resource_delete'),
    
    # Booking URLs
    path('resources/<int:pk>/book/', views.create_booking, name='create_booking'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('my-bookings/<int:pk>/update/', views.update_booking, name='update_booking'),
    path('my-bookings/<int:pk>/cancel/', views.cancel_my_booking, name='cancel_my_booking'),
    path('display_bookings_admin/', views.display_bookings_admin, name='display_bookings_admin'),
    
    path('analytics_booking/', views.analytics_booking, name='analytics_booking'),
]