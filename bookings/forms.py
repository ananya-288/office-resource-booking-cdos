"""Forms for Office Resource Booking System.
User registartion , booking creation and resource management
"""

from django import forms
from django.contrib.auth.models import User
from django.core import validators

from .models import Resource



class UserRegistrationForm(forms.Form):
    """
    Registering a new user along with input validation for all fields.
    """
    # Min and Max length for name
    MIN_LENGTH = 2
    MAX_LENGTH=33

    # Validation messages
    MSG_TOO_SHORT= f"Must have atleast {MIN_LENGTH} characters."
    MSG_TOO_LONG = f"Must have atmost {MAX_LENGTH} characters."
    MSG_LETTERS_ONLY ="Only letters are accepted."

    username =forms.CharField(
        max_length=40,
        validators=[
            validators.MinLengthValidator(3, "Username must have at least 3 characters."),
        ]
    )
    email = forms.EmailField(
        validators=[validators.validate_email]
    )

    first_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(MIN_LENGTH,MSG_TOO_SHORT),
            validators.MaxLengthValidator(MAX_LENGTH, MSG_TOO_LONG),
            validators.RegexValidator(r'\A[a-zA-Z]+\Z',MSG_LETTERS_ONLY)
        ]
    )

    last_name = forms.CharField(
        validators=[
            validators.MinLengthValidator(MIN_LENGTH,MSG_TOO_SHORT),
            validators.MaxLengthValidator(MAX_LENGTH,MSG_TOO_LONG),
            validators.RegexValidator(r'\A[a-zA-Z]+\Z', MSG_LETTERS_ONLY)
        ]
    )

    password = forms.CharField(
        widget=forms.PasswordInput
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput
    )

    def clean_username(self):
        """To check if username is already taken."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean_email(self):
        """To check if email is already registered"""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email

    def clean(self):
        """Check if both the passwords match."""
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data
        
class ResourceForm(forms.ModelForm):
        
    """Resource form for creating and editing office resources accessible by admin"""
    class Meta:
        """Defines the model and fields for the resource form."""
        model = Resource
        fields = ['resource_name', 'resource_type', 'capacity',
                  'location', 'description', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_capacity(self):
        """To validate such that capacity is a positive number"""
        capacity = self.cleaned_data.get('capacity')
        if capacity <= 0:
            raise forms.ValidationError("Capacity must be greater than zero.")
        return capacity

    def clean_resource_name(self):
        """To validate that the resource name is not too short"""
        resource_name = self.cleaned_data.get('resource_name')
        if len(resource_name) < 3:
            raise forms.ValidationError("Resource name must have at least 3 characters.")
        return resource_name    