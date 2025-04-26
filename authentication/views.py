"""
Authentication views for the Dovir Web Application.

This module implements user authentication functionality including login, registration,
profile management, and user statistics. It handles user authentication flows
and profile editing capabilities.
"""

from django import forms
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max
from .models import CustomUser
from .forms import RegisterForm

try:
    from fundraisings.models import Fundraising, Donation, Achievement
except ImportError:
    class Fundraising:
        pass
    class Donation:
        pass
    class Achievement:
        pass


def home(request):
    """
    Render the home page of the application.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered home page template
    """
    user = request.user if request.user.is_authenticated else None
    return render(request, 'index.html', {'user': user})


def login_page(request):
    """
    Handle user authentication and login.
    
    If user is already authenticated, redirects to home page.
    Processes login form, validates credentials and handles errors.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered login page or redirect to home on success
    """
    if request.user.is_authenticated:
        return redirect('/home/')
        
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        user_exists = CustomUser.objects.filter(email=email).exists()
        if not user_exists:
            messages.error(request, 'Користувача з такою електронною поштою не існує')
            return redirect('/login/')
        
        user = CustomUser.objects.get(email=email)
        user = authenticate(username=user.username, password=password)
        
        if user is None:
            messages.error(request, "Неправильний пароль")
            return redirect('/login/')
        else:
            login(request, user)
            return redirect('/home/')
    
    user = request.user if request.user.is_authenticated else None
    return render(request, 'signin.html', {'user': user})


def register_page(request):
    """
    Handle new user registration.
    
    Creates new user accounts with unique usernames based on email addresses.
    Validates form data and automatically logs in new users upon successful registration.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered registration form or redirect to home on success
    """
    if request.user.is_authenticated:
        return redirect('/home/')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = form.cleaned_data['email'].split('@')[0]
            
            base_username = user.username
            counter = 1
            while CustomUser.objects.filter(username=user.username).exists():
                user.username = f"{base_username}{counter}"
                counter += 1
                
            user.set_password(form.cleaned_data['password'])
            
            # Make sure the default avatar path is accessible
            # This ensures media files will work correctly for all users
            from django.conf import settings
            import os
            
            # Check if default avatar file exists and is accessible
            default_avatar_path = os.path.join(settings.MEDIA_ROOT, 'avatars', 'default.png')
            if not os.path.exists(default_avatar_path):
                # If default avatar directory doesn't exist, create it
                os.makedirs(os.path.dirname(default_avatar_path), exist_ok=True)
                
                # Copy default avatar from static files if available
                try:
                    from shutil import copyfile
                    static_default = os.path.join(settings.STATIC_ROOT, 'pictures', 'profile_page', 'default_avatar.png')
                    if os.path.exists(static_default):
                        copyfile(static_default, default_avatar_path)
                except Exception as e:
                    print(f"Could not copy default avatar: {e}")
            
            # Save the user after making sure media paths are sorted
            user.save()
            
            login(request, user)
            return redirect('/home/')
    else:
        form = RegisterForm()
    
    user = request.user if request.user.is_authenticated else None
    return render(request, 'signup.html', {'form': form, 'user': user})


def logout_view(request):
    """
    Log out the current user.
    
    Args:
        request: HTTP request object
        
    Returns:
        Redirect to login page
    """
    logout(request)
    return redirect('/login/')


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    
    Validates and formats social media links and provides form fields for all 
    user profile information.
    """
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'birth_date',
                  'country', 'region', 'city', 'address', 'phone',
                  'avatar', 'instagram', 'facebook', 'telegram']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }
        
    def clean_instagram(self):
        """
        Validate Instagram link format.
        
        Returns:
            Formatted Instagram link
        """
        instagram = self.cleaned_data.get('instagram')
        if instagram:
            if not re.match(r'^https?:\/\/(www\.)?instagram\.com\/.+', instagram, re.I):
                raise forms.ValidationError("Посилання на Instagram має починатися з 'https://instagram.com/'")
        return instagram
        
    def clean_facebook(self):
        """
        Validate Facebook link format.
        
        Returns:
            Formatted Facebook link
        """
        facebook = self.cleaned_data.get('facebook')
        if facebook:
            if not re.match(r'^https?:\/\/(www\.)?facebook\.com\/.+', facebook, re.I):
                raise forms.ValidationError("Посилання на Facebook має починатися з 'https://facebook.com/'")
        return facebook
        
    def clean_telegram(self):
        """
        Validate and format Telegram link.
        
        Returns:
            Properly formatted Telegram link
        """
        telegram = self.cleaned_data.get('telegram')
        if telegram:
            telegram = telegram.strip().lstrip('@')
            if not telegram.startswith('https://t.me/') and not telegram.startswith('http://t.me/'):
                telegram = 'https://t.me/' + telegram
        return telegram


@login_required(login_url='/login/')
def profile_page(request, user_id=None):
    """
    Display user profile page.
    
    Shows user information, fundraisings, donations, and achievements.
    If no user_id is provided, displays the current user's profile.
    
    Args:
        request: HTTP request object
        user_id: Optional user ID to view another user's profile
        
    Returns:
        Rendered profile page
    """
    if user_id:
        profile_user = get_object_or_404(CustomUser, id=user_id)
    elif request.user.is_authenticated:
        profile_user = request.user
    else:
        profile_user = None
    
    is_own_profile = request.user.is_authenticated and (not user_id or request.user.id == user_id)
    
    user_fundraisings = None
    user_achievements = None
    if profile_user:
        try:
            user_fundraisings = Fundraising.objects.filter(creator=profile_user).order_by('-created_at')
            
            user_donations = Donation.objects.filter(user=profile_user).order_by('-date')
            
            all_anonymous = user_donations.exists() and user_donations.filter(anonymous=False).count() == 0
            
            user_donations_display = user_donations.filter(anonymous=False)
            
            try:
                from fundraisings.models import Achievement
                user_achievements = Achievement.check_achievements(profile_user)
            except (ImportError, AttributeError):
                user_achievements = []
                
        except Exception as e:
            print(f"Error in profile page: {e}")
            user_fundraisings = []
            user_donations_display = []
            all_anonymous = False
    else:
        user_fundraisings = None
        user_donations_display = None
        all_anonymous = False
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_fundraisings': user_fundraisings,
        'user_donations': user_donations_display,
        'all_anonymous': all_anonymous,
        'user_achievements': user_achievements
    }
    return render(request, 'profile_page.html', context)


def update_user_statistics(user):
    """
    Update user statistics based on fundraisings and donations.
    
    Calculates and stores metrics like created fundraisings count, 
    total donations, largest donation, etc.
    
    Args:
        user: CustomUser object to update
    """
    try:
        from fundraisings.models import Fundraising, Donation
        
        stats = {
            'created_fundraisings_count': 0,
            'completed_fundraisings_count': 0,
            'total_received_amount': 0,
            'unique_donators_count': 0,
            'supported_fundraisings_count': 0,
            'total_donated_amount': 0,
            'largest_donation_amount': 0
        }
        
        stats['created_fundraisings_count'] = Fundraising.objects.filter(creator=user).count()
        
        try:
            stats['completed_fundraisings_count'] = Fundraising.objects.filter(
                creator=user, status='completed').count()
        except Exception:
            pass
        
        user_fundraising_ids = Fundraising.objects.filter(creator=user).values_list('id', flat=True)
        
        if user_fundraising_ids:
            donations_to_user = Donation.objects.filter(fundraising_id__in=user_fundraising_ids)
            total_received = donations_to_user.aggregate(Sum('amount'))['amount__sum']
            stats['total_received_amount'] = total_received or 0
            stats['unique_donators_count'] = donations_to_user.exclude(
                user=None).values('user').distinct().count()
        
        user_donations = Donation.objects.filter(user=user)
        
        stats['supported_fundraisings_count'] = user_donations.values('fundraising').distinct().count()
        total_donated = user_donations.aggregate(Sum('amount'))['amount__sum']
        stats['total_donated_amount'] = total_donated or 0
        largest_donation = user_donations.aggregate(Max('amount'))['amount__max']
        stats['largest_donation_amount'] = largest_donation or 0
        
        for key, value in stats.items():
            setattr(user, key, value)
            
        user.total_donations_amount = stats['total_donated_amount']
        
        user.save()
    except Exception as e:
        print(f"Error updating user statistics: {e}")


@login_required(login_url='/login/')
def edit_profile(request):
    """
    Handle user profile editing.
    
    Processes form submissions for updating user profile information.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered edit profile form or redirect to profile page on success
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            
            # Special handling for avatar file
            if 'avatar' in request.FILES:
                user.avatar = request.FILES['avatar']
                
            user.save()
            messages.success(request, 'Профіль успішно оновлено!')
            return redirect('profile_page')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form, 'user': request.user})


def categories(request):
    """
    Display categories page.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered categories page
    """
    user = request.user if request.user.is_authenticated else None
    return render(request, 'cats.html', {'user': user})


def about_us(request):
    """
    Display about us page.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered about us page
    """
    user = request.user if request.user.is_authenticated else None
    return render(request, 'about_us.html', {'user': user})


def fundraisings(request):
    """
    Display fundraisings page with optional category filtering.
    
    Args:
        request: HTTP request object
        
    Returns:
        Rendered fundraisings page with filtered results
    """
    from fundraisings.models import Category
    
    category_filter = request.GET.get('category', None)
    
    if category_filter:
        fundraisings_list = Fundraising.objects.filter(categories__name=category_filter)
    else:
        fundraisings_list = Fundraising.objects.all()
        
    categories = Category.objects.all()
    
    context = {
        'fundraisings': fundraisings_list,
        'categories': categories,
        'user': request.user
    }
        
    return render(request, 'fundraisings.html', context)
