"""Forms for Office Resource Booking System.
User registartion , booking creation and resource management
"""

# Third party imports
from django import forms
from django.contrib.auth.models import User
from django.core import validators
from django.utils import timezone

# Local imports
from .models import Resource,Booking




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

    def clean_password(self):
        """
         Checks if the password conains uppercase ,lowecase special character and number.
        """
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 8:
                raise forms.ValidationError(
                   "Password must be minimum 8 characters long."
             )
            if not any(char.isupper() for char in password):
                raise forms.ValidationError(
                  "Password must contain at least one uppercase letter.")
            if not any(char.islower() for char in password):
                raise forms.ValidationError(
                "Password must contain at least one lowercase letter."
             )
            if not any(char.isdigit() for char in password):
                raise forms.ValidationError(
                "Password must contain at least one number."
            )
            if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in password):
                raise forms.ValidationError(
                "Password must contain at least one special character."
            )
        return password

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


class BookingForm(forms.ModelForm):
    """ It is the form for creating bookings and also editing it.Handles conflict detection and includes date validation"""

    class Meta:
        """Defines the model and fields for the booking form."""
        model = Booking
        fields =['resource', 'start_time', 'end_time', 'notes']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time':forms.DateTimeInput(
                attrs={'type': 'datetime-local'},
                format='%Y-%m-%dT%H:%M'
            ),
            'notes':forms.Textarea(attrs={'rows': 3}),
        }
    def __init__(self,*args,**kwargs):
        """Form initialization and setting datetime input formats."""
        super().__init__(*args,**kwargs)
        self.fields['start_time'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_time'].input_formats = ['%Y-%m-%dT%H:%M']
        # It shows only available resources
        self.fields['resource'].queryset = Resource.objects.filter(
           is_available=True)

    def clean_start_time(self):
        """Validates that start time is not in the past."""
        start_time = self.cleaned_data.get('start_time')
        if start_time and start_time < timezone.now():
            raise forms.ValidationError(
                "Start time cannot be in the past."
            )
        return start_time

    def clean_end_time(self):
        """Validates that end time is after start time and makes sure that max duartion is set to 4 hours"""
        end_time = self.cleaned_data.get('end_time')
        start_time = self.cleaned_data.get('start_time')

        if end_time and start_time:
            if end_time <= start_time:
                raise forms.ValidationError(
                    "End time must be after start time."
                )
            # To calculate the duration in hours
            duration= end_time - start_time
            duration_hours =duration.total_seconds() / 3600

            if duration_hours > 4:
                raise forms.ValidationError(
                   "Maximum booking duration is 4 hours."
            )

        return end_time

    def clean(self):
        """Conflict detection --> No two bookings are done for the same resource"""
        cleaned_data = super().clean()
        resource = cleaned_data.get('resource')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')

        if resource and start_time and end_time:
            # To check if there are overlapping bookings
            overlapping_booking = Booking.objects.filter(
                resource=resource,
                status='confirmed',
                start_time__lt=end_time,
                end_time__gt=start_time,
            )
            # Exclude current booking when editing
            if self.instance.pk:
                overlapping_booking = overlapping_booking.exclude(
                    pk=self.instance.pk)
            if overlapping_booking.exists():
                raise forms.ValidationError(
                    "This resource is already booked for the selected time. "
                    "Please choose a different time slot.")
        return cleaned_data
