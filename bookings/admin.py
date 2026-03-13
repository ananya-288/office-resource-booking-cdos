"""
Admin configuration to Registers Resource and Booking models with  admin panel.
"""
from django.contrib import admin
from .models import Resource,Booking

# Controls the way resources are managed in admin panel
@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    """ Admin panel configuration for Resource model"""
    list_display = ['resource_name', 'resource_type','capacity', 'location','is_available']
    list_filter = ['resource_type', 'is_available']
    search_fields = ['resource_name','location']
    sorting = ['resource_name']

# Controls the way bookings are managed in admin panel
@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    """ Admin panel configuration for Booking model """
    list_display = ['user', 'resource','start_time', 'end_time','status', 'created_at']
    list_filter = ['status', 'resource', 'created_at']
    search_fields = ['user__username','resource__resource_name']
    sorting = ['-created_at']
