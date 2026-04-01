"""Tests for booking forms - testing all form validations."""
from django.test import TestCase
from django.contrib.auth.models import User
from bookings.forms import UserRegistrationForm, BookingForm, ResourceForm


class TestRegistrationForm(TestCase):
    """Testing the registration form validation."""

    def test_valid_registration_form(self):
        """Check that a valid form passes validation."""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        })
        self.assertTrue(form.is_valid())

    def test_password_mismatch(self):
        """Check that mismatched passwords fail validation."""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Test@1234',
            'confirm_password': 'Different@1234'
        })
        self.assertFalse(form.is_valid())

    def test_weak_password_fails(self):
        """Check that a weak password fails validation."""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'test@test.com',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'weakpass',
            'confirm_password': 'weakpass'
        })
        self.assertFalse(form.is_valid())

    def test_missing_email_fails(self):
        """Check that missing email fails validation."""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': '',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        })
        self.assertFalse(form.is_valid())

    def test_invalid_email_fails(self):
        """Check that invalid email format fails validation."""
        form = UserRegistrationForm(data={
            'username': 'testuser',
            'email': 'notanemail',
            'first_name': 'Test',
            'last_name': 'User',
            'password': 'Test@1234',
            'confirm_password': 'Test@1234'
        })
        self.assertFalse(form.is_valid())


class TestBookingForm(TestCase):
    """Testing the booking form validation."""

    def setUp(self):
        """Create test user and resource for booking tests."""
        from bookings.models import Resource
        self.user = User.objects.create_user(
            username='testuser',
            password='Test@1234',
            email='test@test.com'
        )
        self.resource = Resource.objects.create(
            resource_name='Test Room',
            resource_type='meeting_room',
            capacity=10,
            location='Floor 1',
            is_available=True
        )

    def test_valid_booking_form(self):
        """Check that a valid booking form passes validation."""
        from django.utils import timezone
        from datetime import timedelta
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        form = BookingForm(data={
            'resource': self.resource.pk,
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
            'notes': 'Test booking'
        })
        self.assertTrue(form.is_valid())

    def test_booking_exceeds_max_duration(self):
        """Check that booking exceeding 4 hours fails validation."""
        from django.utils import timezone
        from datetime import timedelta
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=5)
        form = BookingForm(data={
            'resource': self.resource.pk,
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
            'notes': 'Test booking'
        })
        self.assertFalse(form.is_valid())

    def test_booking_end_before_start_fails(self):
        """Check that booking with end time before start fails."""
        from django.utils import timezone
        from datetime import timedelta
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time - timedelta(hours=1)
        form = BookingForm(data={
            'resource': self.resource.pk,
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
            'notes': 'Test booking'
        })
        self.assertFalse(form.is_valid())

    def test_booking_in_past_fails(self):
        """Check that booking with past start time fails."""
        from django.utils import timezone
        from datetime import timedelta
        start_time = timezone.now() - timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        form = BookingForm(data={
            'resource': self.resource.pk,
            'start_time': start_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': end_time.strftime('%Y-%m-%dT%H:%M'),
            'notes': 'Test booking'
        })
        self.assertFalse(form.is_valid())



















































