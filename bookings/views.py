""" Views for the Office Resource Booking System . """

# Standard library imports
import logging
from datetime import timedelta
import json

# Third party imports
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count


# Local imports
from .models import Resource, Booking
from .forms import UserRegistrationForm,ResourceForm,BookingForm


# Get logger for this module
logger =logging.getLogger(__name__)

# Common message constants
MSG_RESOURCE_NOT_FOUND = 'Resource not found.'
MSG_ACCESS_RESTRICTED = 'Access restricted to administrators only.'
MSG_BOOKING_NOT_FOUND = 'Booking not found.'

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
            User.objects.create_user(
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
            logger.info('New user registered: %s', username)
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
            logger.info('User logged in successfully')
            messages.success(request, f'Hello {user.first_name}, welcome back')
            # If specified redirect to next page
            next_page = request.POST.get('next') or request.GET.get('next')
            # Validating next_page
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect('home')
        logger.warning('Login attempt failed for user')
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
    logger.info('User logged out.')
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
        messages.error(request, MSG_RESOURCE_NOT_FOUND)
        return redirect('list_resources')
    return render(request, 'bookings/resource_detail.html', {'resource': resource})


@login_required
def resource_create(request):
    """
    Only admin can add new resource and regular user are given error message.
    """
    # Only admins can add resources
    if not request.user.is_staff:
        messages.error(request, MSG_ACCESS_RESTRICTED)
        return redirect('list_resources')

    if request.method == 'POST':
        form = ResourceForm(request.POST)
        if form.is_valid():
            form.save()
            logger.info('Resource created by admin: %s', request.user.username)
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
        messages.error(request,MSG_ACCESS_RESTRICTED)
        return redirect('list_resources')
    try:
        resource =Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request, MSG_RESOURCE_NOT_FOUND)
        return redirect('list_resources')
    if request.method == 'POST':
        form =ResourceForm(request.POST, instance=resource)
        if form.is_valid():
            form.save()
            logger.info('Resource updated by admin: %s', request.user.username)
            messages.success(request,'Resource details have been updated.')
            return redirect('list_resources')
    else:
        form = ResourceForm(instance=resource)
    return render(request,'bookings/resource_form.html', {
        'form': form,
        'title': 'Edit Resource'})



@login_required
def resource_delete(request, pk):
    """
    Allows administrators to delete a resource.
    """
    if not request.user.is_staff:
        messages.error(request, MSG_ACCESS_RESTRICTED)
        return redirect('list_resources')

    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request, MSG_RESOURCE_NOT_FOUND)
        return redirect('list_resources')

    if request.method == 'POST':
        resource.delete()
        logger.info('Resource deleted by admin: %s', request.user.username)
        messages.success(request, 'Resource successfully deleted.')
        return redirect('list_resources')

    return render(request, 'bookings/delete_resource.html', {'resource': resource})


@login_required
def create_booking(request, pk):
    """This function handles the creation of new booking and sends confirmation email on successful booking."""
    try:
        resource =Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        messages.error(request,MSG_RESOURCE_NOT_FOUND)
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
            logger.info('Booking created by user: %s for resource: %s',request.user.username,new_booking.resource.resource_name)

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
        messages.error(request, MSG_BOOKING_NOT_FOUND)
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
            # Send update confirmation email
            send_mail(
                subject='Booking Updated - ORBS',
                message=f'Hello {request.user.first_name},\n\n'
                        f'Your booking has been updated.\n\n'
                        f'Resource: {existing_booking.resource.resource_name}\n'
                        f'New Start: {existing_booking.start_time}\n'
                        f'New End: {existing_booking.end_time}\n\n'
                        f'Regards,\nORBS Team',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email],
            fail_silently=True,
            )
            logger.info('Booking updated by user: %s', request.user.username)
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
        messages.error(request, MSG_BOOKING_NOT_FOUND)
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
        logger.info('Booking cancelled by user: %s for the resource: %s',request.user.username,booking_to_cancel.resource.resource_name)

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
        messages.error(request, MSG_ACCESS_RESTRICTED)
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


def get_resource_stats(today):
    """Calculate resource statistics for analytics dashboard."""
    total_resources = Resource.objects.count()
    available_resources = Resource.objects.filter(is_available=True).count()
    todays_bookings = Booking.objects.filter(
        start_time__date=today,
        status='confirmed'
    ).count()
    most_popular = Resource.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count').first()
    resource_utilisation = Resource.objects.annotate(
        booking_count=Count('booking')
    ).order_by('-booking_count')
    return (total_resources, available_resources,
            todays_bookings, most_popular, resource_utilisation)


def get_booking_stats():
    """To calculate booking stats"""
    total_bookings =Booking.objects.count()
    cancelled_bookings = Booking.objects.filter(status='cancelled').count()
    confirmed_bookings =Booking.objects.filter(status='confirmed').count()
    if total_bookings> 0:
        cancellation_rate = round((cancelled_bookings / total_bookings) * 100, 1)
    else:
        cancellation_rate = 0
    return total_bookings, cancelled_bookings, confirmed_bookings, cancellation_rate


def get_peak_hour():
    """To calculate peak booking hour."""
    all_bookings = Booking.objects.filter(
        status='confirmed'
    ).select_related('resource', 'user')
    hour_counts = {}
    for booking in all_bookings:
        hour =booking.start_time.hour
        hour_counts[hour] = hour_counts.get(hour, 0) + 1
    if hour_counts:
        peak_hour =max(hour_counts, key=hour_counts.get)
        return f"{peak_hour:02d}:00 - {peak_hour+1:02d}:00"
    return 'No data yet'


def get_weekly_trend():
    """Calculate booking trend this week v/s last week."""
    today =timezone.now().date()
    week_start = today - timedelta(days=today.weekday())
    last_week_start =week_start - timedelta(days=7)
    this_week = Booking.objects.filter(
        created_at__date__gte=week_start,
        status='confirmed'
    ).select_related('resource', 'user').count()
    last_week = Booking.objects.filter(
        created_at__date__gte=last_week_start,
        created_at__date__lt=week_start,
        status='confirmed'
    ).select_related('resource','user').count()
    if last_week > 0:
        trend =round(((this_week - last_week) /last_week) * 100, 1)
    else:
        trend = 0
    return this_week, last_week,trend


def get_chart_data(resource_utilisation):
    """Prepare chart data for analytics dashboard."""
    chart_labels=json.dumps([r.resource_name for r in resource_utilisation])
    chart_data =json.dumps([r.booking_count for r in resource_utilisation])
    return chart_labels,chart_data


@login_required
def analytics_booking(request):
    """
    Displays resource usage analytics and insights.Only admins can see this.
    """
    if not request.user.is_staff:
        messages.error(request, MSG_ACCESS_RESTRICTED)
        return redirect('home')
    today =timezone.now().date()
    res_stats =get_resource_stats(today)
    book_stats = get_booking_stats()
    chart_labels, chart_data = get_chart_data(res_stats[4])

    logger.info('Analytics dashboard accessed by admin: %s', request.user.username)

    context = {
        'total_resources': res_stats[0],
        'available_resources': res_stats[1],
        'todays_bookings': res_stats[2],
        'most_popular': res_stats[3],
        'resource_utilisation': res_stats[4],
        'total_bookings': book_stats[0],
        'cancelled_bookings': book_stats[1],
        'confirmed_bookings': book_stats[2],
        'cancellation_rate': book_stats[3],
        'peak_hour_display': get_peak_hour(),
        'this_week_bookings': get_weekly_trend()[0],
        'last_week_bookings': get_weekly_trend()[1],
        'trend': get_weekly_trend()[2],
        'chart_labels': chart_labels,
        'chart_data': chart_data,
    }
    return render(request, 'bookings/analytics.html', context)
    