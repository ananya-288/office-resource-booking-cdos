"""Tests written for Office Resource Booking System."""

from mixer.backend.django import mixer
import pytest

@pytest.mark.django_db
class TestResourceModel:
    """Tests for Resource model."""

    def test_resource_created(self):
        """Test to check if the resource is created successfully"""
        resource =mixer.blend('bookings.Resource',resource_name='Test Room',
                               capacity=10)
        assert resource.resource_name =='Test Room'

    def test_resource_capacity_positive(self):
        """To test capacity is positive."""
        resource= mixer.blend('bookings.Resource', capacity=5)
        assert resource.capacity > 0

    def test_resource_available_default(self):
        """To test resource is available by default."""
        resource =mixer.blend('bookings.Resource')
        assert resource.is_available is True
        
    def test_resource_string_representation(self):
        resource= mixer.blend('bookings.Resource',resource_name='Conference Room A',resource_type='meeting_room')
        assert 'Conference Room A' in str(resource)


@pytest.mark.django_db
class TestBookingModel:
    """Tests for the Booking model."""

    def test_booking_created(self):
        """Test that a booking can be created successfully."""
        booking = mixer.blend('bookings.Booking')
        assert booking.pk is not None

    def test_booking_status_confirmed(self):
        """To test booking is available by default."""
        booking =mixer.blend('bookings.Booking', status='confirmed')
        assert booking.status == 'confirmed'

    def test_booking_can_be_cancelled(self):
        booking = mixer.blend('bookings.Booking', status='confirmed')
        booking.status = 'cancelled'
        booking.save()
        assert booking.status == 'cancelled'
    def test_booking_string_representation(self):
        """Test the string representation of a booking."""
        booking =mixer.blend('bookings.Booking')
        assert booking.resource.resource_name in str(booking)