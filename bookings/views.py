""" Views for the Office Resource Booking System . """
from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import UserRegistrationForm

from django.contrib.auth.decorators import login_required
from .models import Resource, Booking
from .forms import UserRegistrationForm, ResourceForm


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


@login_required
def list_resources(request):
    """All the available resources are displayed along with search and filter functionality."""
    
    resources = Resource.objects.filter(is_available=True)
    resource_type = request.GET.get('resource_type', '')
    min_capacity = request.GET.get('min_capacity', '')
    search_query = request.GET.get('search', '')
    if resource_type:
        resources = resources.filter(resource_type=resource_type)
    if min_capacity:
        resources = resources.filter(capacity__gte=min_capacity)
    if search_query:
        resources = resources.filter(resource_name__icontains=search_query)
    context = {
        'resources': resources,
        'resource_types': Resource.RESOURCE_TYPES,
        'selected_type':resource_type,
        'min_capacity': min_capacity,
        'search_query':search_query,
    }
    return render(request, 'bookings/resource_list.html', context)


@login_required
def resource_detail(request, pk):
    """
    Displays the details of a specific resource.
    """
    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request, 'Resource not found.')
        return redirect('list_resources')
    return render(request, 'bookings/resource_detail.html', {'resource': resource})


@login_required
def resource_create(request):
    """
    Only admin can add new resource and regular user are given error message.
    """
    # Only admins can add resources
    if not request.user.is_staff:
        messages.error(request, 'Access restricted to administrators only.')
        return redirect('list_resources')

    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resource has been added to the system.')
            return redirect('list_resources')
    else:
        form = ResourceForm()

    return render(request,'bookings/resource_form.html', {
        'form': form,
        'title': 'Add New Resource'
    })


@login_required
def resource_edit(request, pk):
    """
    Allows administrators to edit an existing resource.
    """
    if not request.user.is_staff:
        messages.error(request,'Access restricted to administrators only.')
        return redirect('list_resources')
    try:
        resource =Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request, 'Resource not found.')
        return redirect('list_resources')
    if request.method == 'POST':
        form =ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            messages.success(request,'Resource details have been updated.')
            return redirect('list_resources')
    else:
        form = ResourceForm(instance=resource)
    return render(request,'bookings/resource_form.html', {
        'form': form,
        'title': 'Edit Resource'})


@login_required
@login_required
def resource_delete(request, pk):
    """
    Allows administrators to delete a resource.
    """
    if not request.user.is_staff:
        messages.error(request, 'Access restricted to administrators only.')
        return redirect('list_resources')

    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request, 'Resource not found.')
        return redirect('list_resources')

    if request.method == 'POST':
        resource.delete()
        messages.success(request, 'Resource successfully deleted.')
        return redirect('list_resources')

    return render(request, 'bookings/delete_resource.html', {'resource': resource})
