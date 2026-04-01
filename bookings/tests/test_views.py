"""
Tests for views - making sure all the main pages
and actions in the application are working as expected.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from bookings.models import Resource, Booking
from django.utils import timezone
from datetime import timedelta

TEST_USERNAME = 'testuser'
TEST_PASS = 'Test@1234'  # nosonar
TEST_EMAIL = 'test@test.com'
TEST_FIRST_NAME = 'Test'
TEST_LAST_NAME = 'User'
NEW_USERNAME = 'newuser'
NEW_EMAIL = 'newuser@test.com'
NEW_PASS = 'NewUser@1234'  # nosonar


class TestViews(TestCase):
    """
    Testing the views of the application.
    I created a test user and resource in setUp so I can reuse
    them across all tests without repeating the same code.
    """

    def setUp(self):
        """Create a test user, client and resource before each test."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            password=TEST_PASS,  # nosonar
            email=TEST_EMAIL,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
        )
        self.resource = Resource.objects.create(
            resource_name='Test Room',
            resource_type='meeting_room',
            capacity=10,
            location='Floor 1',
            is_available=True
        )

    def test_home_redirects_unauthenticated_user(self):
        """
        If someone tries to access the home page without logging in
        they should be redirected to the login page.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 302)

    def test_home_loads_for_authenticated_user(self):
        """
        Once logged in the user should be able to see the home page
        without any issues.
        """
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """
        The login page should be accessible to everyone
        even without being logged in.
        """
        response = self.client.get(reverse('login_user'))
        self.assertEqual(response.status_code, 200)

    def test_register_page_loads(self):
        """
        The registration page should be accessible to everyone
        so new users can sign up.
        """
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_resource_list_redirects_unauthenticated_user(self):
        """
        Users who are not logged in should not be able to
        see the resources list and should be redirected.
        """
        response = self.client.get(reverse('list_resources'))
        self.assertEqual(response.status_code, 302)

    def test_resource_list_loads_for_authenticated_user(self):
        """
        Logged in users should be able to browse
        the available office resources.
        """
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('list_resources'))
        self.assertEqual(response.status_code, 200)

    def test_my_bookings_redirects_unauthenticated_user(self):
        """
        The my bookings page should not be accessible
        to users who are not logged in.
        """
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 302)

    def test_my_bookings_loads_for_authenticated_user(self):
        """
        Logged in users should be able to view
        their own bookings without any issues.
        """
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_user(self):
        """
        After logging out the user should be redirected
        away from the application.
        """
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('logout_user'))
        self.assertEqual(response.status_code, 302)

    def test_login_with_correct_credentials_redirects(self):
        """
        When a user logs in with the correct username and password
        they should be redirected to the home page.
        """
        response = self.client.post(reverse('login_user'), {
            'username': TEST_USERNAME,
            'password': TEST_PASS
        })
        self.assertEqual(response.status_code, 302)

    def test_login_with_wrong_credentials_stays_on_page(self):
        """
        If someone tries to log in with a wrong password
        they should stay on the login page and see an error.
        """
        response = self.client.post(reverse('login_user'), {
            'username': TEST_USERNAME,
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_register_with_valid_data_redirects(self):
        """
        When someone registers with valid details
        they should be redirected after successful registration.
        """
        response = self.client.post(reverse('register'), {
            'username': NEW_USERNAME,
            'email': NEW_EMAIL,
            'first_name': TEST_FIRST_NAME,
            'last_name': TEST_LAST_NAME,
            'password': NEW_PASS,
            'confirm_password': NEW_PASS
        })
        self.assertEqual(response.status_code, 302)

    def test_analytics_redirects_non_admin(self):
        """Check that non admin users cannot access analytics."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('analytics_booking'))
        self.assertEqual(response.status_code, 302)

    def test_analytics_accessible_for_admin(self):
        """Check that admin users can access analytics dashboard."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('analytics_booking'))
        self.assertEqual(response.status_code, 200)

    def test_admin_bookings_redirects_non_admin(self):
        """Check that non admin users cannot access admin bookings."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('display_bookings_admin'))
        self.assertEqual(response.status_code, 302)

    def test_admin_bookings_accessible_for_admin(self):
        """Check that admin can access the admin bookings page."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('display_bookings_admin'))
        self.assertEqual(response.status_code, 200)

    def test_resource_create_redirects_non_admin(self):
        """Check that non admin users cannot create resources."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('resource_create'))
        self.assertEqual(response.status_code, 302)

    def test_resource_create_accessible_for_admin(self):
        """Check that admin users can access resource create page."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(reverse('resource_create'))
        self.assertEqual(response.status_code, 200)

    def test_resource_create_post_by_admin(self):
        """Check that admin can create a resource via POST."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.post(reverse('resource_create'), {
            'resource_name': 'New Room',
            'resource_type': 'meeting_room',
            'capacity': 10,
            'location': 'Floor 1',
            'description': 'A test room',
            'is_available': True
        })
        self.assertEqual(response.status_code, 302)

    def test_make_booking_page_loads(self):
        """Check that the make booking page loads for logged in users."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(
            reverse('create_booking', args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_resource_detail_loads(self):
        """Check that resource detail page loads correctly."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(
            reverse('resource_detail', args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_resource_edit_accessible_for_admin(self):
        """Check that admin can access resource edit page."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(
            reverse('resource_edit', args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_resource_delete_accessible_for_admin(self):
        """Check that admin can access resource delete page."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.get(
            reverse('resource_delete', args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_resource_delete_post_by_admin(self):
        """Check that admin can delete a resource via POST."""
        self.user.is_staff = True
        self.user.save()
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        response = self.client.post(
            reverse('resource_delete', args=[self.resource.pk])
        )
        self.assertEqual(response.status_code, 302)

    def test_update_booking_page_loads(self):
        """Check that the update booking page loads for logged in users."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        booking = Booking.objects.create(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        response = self.client.get(
            reverse('update_booking', args=[booking.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_cancel_booking_page_loads(self):
        """Check that the cancel booking page loads for logged in users."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        booking = Booking.objects.create(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        response = self.client.get(
            reverse('cancel_my_booking', args=[booking.pk])
        )
        self.assertEqual(response.status_code, 200)

    def test_cancel_booking_post(self):
        """Check that user can cancel their booking via POST."""
        self.client.login(username=TEST_USERNAME, password=TEST_PASS)
        start_time = timezone.now() + timedelta(days=1)
        end_time = start_time + timedelta(hours=2)
        booking = Booking.objects.create(
            user=self.user,
            resource=self.resource,
            start_time=start_time,
            end_time=end_time,
            status='confirmed'
        )
        response = self.client.post(
            reverse('cancel_my_booking', args=[booking.pk])
        )
        self.assertEqual(response.status_code, 302)