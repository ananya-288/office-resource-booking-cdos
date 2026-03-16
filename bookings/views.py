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

from .forms import UserRegistrationForm,ResourceForm,BookingForm

from django.utils import timezone


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
    This function will handle user login. It will redirect to next page if specificed or else it goes to home.
    """
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        # Authenticate the user
        user =authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Hello {user.first_name}, welcome back')
            # If specified redirect to next page
            next_page = request.POST.get('next') or request.GET.get('next')
            if next_page:
                return redirect(next_page)
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


@login_required
def create_booking(request, pk):
    """This function handles the creation of new booking and sends confirmation email on successful booking."""
    try:
        resource =Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request,'Resource not found.')
        return redirect('list_resources')
    if request.method =='POST':
        form =BookingForm(request.POST)
        if form.is_valid():
              # Create booking but do not sav eit now
            new_booking = form.save(commit=False)
            # Current user is assigned to the booking
            new_booking.user = request.user
            # To calculate the duration in hours
            duration =new_booking.end_time - new_booking.start_time
            new_booking.duration_hours =duration.total_seconds() / 3600
            new_booking.save()

            # Sending confirmation email
            send_mail(
                subject='Booking Confirmation - Office Resource Booking System',
                message=f'Hello {request.user.first_name},\n\n'
                        f'Your booking has been confirmed.\n\n'
                        f'Resource: {new_booking.resource.resource_name}\n'
                        f'Start: {new_booking.start_time}\n'
                        f'End: {new_booking.end_time}\n\n'
                        f'Regards,\nORBS Team',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email],
                fail_silently=True,
            )
            messages.success(request, 'Your booking has been confirmed!')
            return redirect('my_bookings')
    else:
        # Pre-select the resource in the form
        form = BookingForm(initial={'resource': resource})

    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'resource': resource,
    })


@login_required
def my_bookings(request):
    """
    To display all the bookings of the user currently logged in. 
    It also categorises bookings into upcoming,active and past.
    """
    current_time = timezone.now()

    # Getting the current user's confirmed bookings
    all_bookings = Booking.objects.filter(
        user=request.user
    ).order_by('start_time')
    # Categorise bookings
    upcoming_bookings = all_bookings.filter(
        status='confirmed',
        start_time__gt=current_time
    )
    active_bookings = all_bookings.filter(
        status='confirmed',
        start_time__lte=current_time,
        end_time__gte=current_time
    )
    past_bookings = all_bookings.filter(
        end_time__lt=current_time
    ) | all_bookings.filter(status='cancelled')

    context = {
        'upcoming_bookings':upcoming_bookings,
        'active_bookings': active_bookings,
        'past_bookings': past_bookings,
    }
    return render(request, 'bookings/booking_list.html', context)


@login_required
def update_booking(request, pk):
    """
    Allows users to edit their existing bookings.
    Prevents editing of bookings that have already started.
    """
    try:
        existing_booking = Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('my_bookings')

    # Prevent editing bookings that have already started
    if existing_booking.start_time <= timezone.now():
        messages.error(request, 'Unable to edit a booking that is already in progress.')
        return redirect('my_bookings')
        
    # Prevent editing bookings within 1 hour of start time
    time_until_start = existing_booking.start_time - timezone.now()
    if time_until_start.total_seconds() < 3600:
        messages.error(
           request,
             'Bookings cannot be edited within 1 hour of the start time.' )
        return redirect('my_bookings')    

    if request.method == 'POST':
        form = BookingForm(request.POST, instance=existing_booking)
        if form.is_valid():
            form.save()
            messages.success(request, 'Booking details updated successfully.')
            return redirect('my_bookings')
    else:
        form = BookingForm(instance=existing_booking)

    return render(request, 'bookings/booking_form.html', {
        'form': form,
        'resource': existing_booking.resource,
    })
    
    


@login_required
def cancel_my_booking(request, pk):
    """
    The users can cancel their existing bookings and email is sent for successful cancellation.
    The cancellation cannot be done within 1 hour of start time.
    """
    try:
        booking_to_cancel =Booking.objects.get(pk=pk, user=request.user)
    except Booking.DoesNotExist:
        messages.error(request, 'Booking not found.')
        return redirect('my_bookings')
    # Prevent cancellation within 1 hour of start time
    time_until_start = booking_to_cancel.start_time - timezone.now()
    if time_until_start.total_seconds() < 3600:
        messages.error(
            request,
            'Bookings cannot be cancelled within 1 hour of the start time.'
        )
        return redirect('my_bookings')
    if request.method =='POST':
        booking_to_cancel.status ='cancelled'
        booking_to_cancel.save()

        # Send cancellation email
        send_mail(
            subject='Booking Cancellation - Office Resource Booking System',
            message=f'Hello {request.user.first_name},\n\n'
                    f'Your booking has been cancelled.\n\n'
                    f'Resource: {booking_to_cancel.resource.resource_name}\n'
                    f'Start: {booking_to_cancel.start_time}\n'
                    f'End: {booking_to_cancel.end_time}\n\n'
                    f'Regards,\nORBS Team',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True,
        )
        messages.success(request, 'Your booking has been cancelled.')
        return redirect('my_bookings')

    return render(request, 'bookings/cancel_booking.html', {
        'booking': booking_to_cancel
    })
    
@login_required
def display_bookings_admin(request):
    """
    This method is to display all booking made by all users. Only admin can access.
    """
    if not request.user.is_staff:
        messages.error(request, 'Access restricted to administrators only.')
        return redirect('home')

    # Most recent is fetched first and getting all bookings.
    all_bookings = Booking.objects.all().order_by('-created_at')

    # Filtering by status if provided
    status_filter =request.GET.get('status', '')
    if status_filter:
        all_bookings =all_bookings.filter(status=status_filter)

    context = {
        'all_bookings': all_bookings,
        'status_filter': status_filter,
    }
    return render(request, 'bookings/admin_bookings.html', context)