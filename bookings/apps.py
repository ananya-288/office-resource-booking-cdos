"""
Config for the orbs bookings app. 
"""

from django.apps import AppConfig


class BookingsConfig(AppConfig):
    """Class for the bookings app --> configuration."""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bookings'
