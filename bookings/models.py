"""
Resource and Booking model to manage office resources
"""

from django.db import models
from django.contrib.auth.models import User # Using Django's user model


#Stores the resource info
class Resource(models.Model):
    """ Office resources which the user can book """

    # Options Resource type can have
    RESOURCE_TYPES = [
        ('desk', 'Desk'),
        ('meeting_room', 'Meeting Room'),
        ('huddle_room' , 'Huddle Room'),
        ('lockers', 'Lockers'),
       ]
    resource_name = models.CharField(max_length=80)
    resource_type = models.CharField(max_length=30,choices=RESOURCE_TYPES)
    description = models.TextField(blank=True)
    capacity = models.IntegerField()
    location = models.CharField(max_length=60)
    is_available = models.BooleanField(default=True)
    created_at =models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.resource_name}({self.get_resource_type_display()})"

#Stores the booking reservation done by user
class Booking(models.Model):
    """ Represents booking made by user for a specific resource."""

    # Options for Booking status
    STATUS_CHOICES = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
       ]
    # Links booking to a specific user and resource
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time= models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='confirmed')
    notes = models.TextField(blank=True)
    created_at =models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}-{self.resource.resource_name}({self.start_time})"
