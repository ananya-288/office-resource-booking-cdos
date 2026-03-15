""" Views for the Office Resource Booking System . """
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm


def register(request):
    """
    Method to register a new user and send email on successful registartion
    """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Taking the data from form after validation
            username = form.cleaned_data['username']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            password = form.cleaned_data['password']

            # Creating the new account
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=password
            )

            # Sending email
            send_mail(
                subject='Welcome to ORBS',
                message=f'Hello {first_name},\n\nWelcome to the Office Resource Booking System.\n\nRegards,\nORBS Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=True,
            )
            messages.success(request, 'You have been successfully registered. Please log in')
            return redirect('login_user')
    else:
        form=UserRegistrationForm()

    return render(request,'bookings/register.html', {'form': form})


def login_user(request):
    """
    Authenticates user credentials and creates a session.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Hello {user.first_name}, welcome back!')
            return redirect('home')
        else:
            messages.error(request, 'Incorrect username or password. Please try again.')
    return render(request, 'bookings/login.html')
    
def home(request):
    """
    Home page of the application is rendered
    """
    return render(request, 'bookings/home.html')


def logout_user(request):
    """
    Clearing the user session and redirecting to login page.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login_user')


