"""
Url's for testing
"""

from django.urls import reverse,resolve

class TestUrls:
    """Tests for the URL config."""

    def test_home_url(self):
        """Test that home URL resolves correctly"""
        path = reverse('home')
        assert resolve(path).view_name == 'home'

    def test_register_url(self):
        """This is for register URL"""
        path = reverse('register')
        assert resolve(path).view_name == 'register'

    def test_login_url(self):
        """This is for login URL"""
        path = reverse('login_user')
        assert resolve(path).view_name == 'login_user'

    def test_logout_url(self):
        """This is for logout URL"""
        path = reverse('logout_user')
        assert resolve(path).view_name == 'logout_user'

    def test_resource_list_url(self):
        """This is for list URL"""
        path = reverse('list_resources')
        assert resolve(path).view_name == 'list_resources'

    def test_resource_detail_url(self):
        """This is for resourcedtail URL"""
        path = reverse('resource_detail', kwargs={'pk': 1})
        assert resolve(path).view_name == 'resource_detail'

    def test_create_resource_url(self):
        """It is for create resource URL"""
        path = reverse('resource_create')
        assert resolve(path).view_name == 'resource_create'

    def test_my_bookings_url(self):
        """This is for bookings URL"""
        path = reverse('my_bookings')
        assert resolve(path).view_name == 'my_bookings'

    def test_analytics_url(self):
        """To check that analytics resolves correctly"""
        path = reverse('analytics_booking')
        assert resolve(path).view_name == 'analytics_booking'

    def test_admin_bookings_url(self):
        """Test that admin bookings URL resolves correctly."""
        path = reverse('display_bookings_admin')
        assert resolve(path).view_name == 'display_bookings_admin'