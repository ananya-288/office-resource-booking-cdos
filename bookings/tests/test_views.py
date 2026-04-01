"""
Tests for views 
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User

# Using constants so I dont have to repeat the same strings everywhere
TEST_USERNAME = 'testuser'
TEST_PASSWORD = 'Test@1234'
TEST_EMAIL = 'test@test.com'
TEST_FIRST_NAME = 'Test'
TEST_LAST_NAME = 'User'
NEW_USERNAME = 'newuser'
NEW_EMAIL = 'newuser@test.com'
NEW_PASSWORD = 'NewUser@1234'


class TestViews(TestCase):
    """
    Testing the views of the application.
    I created a test user in setUp so I can use it across all tests
    without having to create one in each test method.
    """

    def setUp(self):
        """Create a test user and client before running each test."""
        self.client = Client()
        self.user = User.objects.create_user(
            username=TEST_USERNAME,
            password=TEST_PASSWORD,
            email=TEST_EMAIL,
            first_name=TEST_FIRST_NAME,
            last_name=TEST_LAST_NAME
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
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
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
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
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
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        response = self.client.get(reverse('my_bookings'))
        self.assertEqual(response.status_code, 200)

    def test_logout_redirects_user(self):
        """
        After logging out the user should be redirected
        away from the application.
        """
        self.client.login(username=TEST_USERNAME, password=TEST_PASSWORD)
        response = self.client.get(reverse('logout_user'))
        self.assertEqual(response.status_code, 302)

    def test_login_with_correct_credentials_redirects(self):
        """
        When a user logs in with the correct username and password
        they should be redirected to the home page.
        """
        response = self.client.post(reverse('login_user'), {
            'username': TEST_USERNAME,
            'password': TEST_PASSWORD
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
            'password': NEW_PASSWORD,
            'confirm_password': NEW_PASSWORD
        })
        self.assertEqual(response.status_code, 302)