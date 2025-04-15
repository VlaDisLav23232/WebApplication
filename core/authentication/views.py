#Changed by claude



# Import necessary modules and models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max
from .models import CustomUser
from .forms import RegisterForm
from django import forms
import re

# Try to import Fundraising and Donation models - with error handling to avoid import errors
try:
    from fundraisings.models import Fundraising, Donation
except ImportError:
    # If the import fails, create placeholder classes for type hints only
    class Fundraising:
        pass
    class Donation:
        pass

# Define a view function for the home page
def home(request):
    user = request.user if request.user.is_authenticated else None
    return render(request, 'index.html', {'user': user})

# Define a view function for the login page
def login_page(request):
    # Якщо користувач вже авторизований, перенаправляємо на головну
    if request.user.is_authenticated:
        return redirect('/home/')
        
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check if a user with the provided email exists
        user_exists = CustomUser.objects.filter(email=email).exists()
        if not user_exists:
            messages.error(request, 'Користувача з такою електронною поштою не існує')
            return redirect('/login/')
        
        # Get the user with the provided email
        user = CustomUser.objects.get(email=email)
        
        # Authenticate the user with username and password
        user = authenticate(username=user.username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Неправильний пароль")
            return redirect('/login/')
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('/home/')
    
    # Render the login page template (GET request)
    user = request.user if request.user.is_authenticated else None
    return render(request, 'signin.html', {'user': user})

# Define a view function for the registration page
def register_page(request):
    # Якщо користувач вже авторизований, перенаправляємо на головну
    if request.user.is_authenticated:
        return redirect('/home/')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Generate username from email (before the @ symbol)
            user.username = form.cleaned_data['email'].split('@')[0]
            # Check if username exists and make it unique if needed
            base_username = user.username
            counter = 1
            while CustomUser.objects.filter(username=user.username).exists():
                user.username = f"{base_username}{counter}"
                counter += 1
                
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Автоматично авторизуємо користувача
            login(request, user)
            return redirect('/home/')  # Перенаправляємо на головну сторінку
    else:
        form = RegisterForm()
    
    user = request.user if request.user.is_authenticated else None
    return render(request, 'signup.html', {'form': form, 'user': user})

# Функція для виходу з облікового запису
def logout_view(request):
    logout(request)
    # Redirect without showing messages from previous pages
    return redirect('/login/')


class ProfileUpdateForm(forms.ModelForm):
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
        instagram = self.cleaned_data.get('instagram')
        if instagram:
            if not re.match(r'^https?:\/\/(www\.)?instagram\.com\/.+', instagram, re.I):
                raise forms.ValidationError("Посилання на Instagram має починатися з 'https://instagram.com/'")
        return instagram
        
    def clean_facebook(self):
        facebook = self.cleaned_data.get('facebook')
        if facebook:
            if not re.match(r'^https?:\/\/(www\.)?facebook\.com\/.+', facebook, re.I):
                raise forms.ValidationError("Посилання на Facebook має починатися з 'https://facebook.com/'")
        return facebook
        
    def clean_telegram(self):
        telegram = self.cleaned_data.get('telegram')
        if telegram:
            # Видаляємо @ якщо користувач додав його
            telegram = telegram.strip().lstrip('@')
            # Додаємо https://t.me/ якщо його немає
            if not telegram.startswith('https://t.me/') and not telegram.startswith('http://t.me/'):
                telegram = 'https://t.me/' + telegram
        return telegram

# Оновлена функція profile_page
@login_required(login_url='/login/')
def profile_page(request, user_id=None):
    # Get the profile user (either the requested user or the current user)
    if user_id:
        profile_user = get_object_or_404(CustomUser, id=user_id)
    elif request.user.is_authenticated:
        profile_user = request.user
    else:
        profile_user = None
    
    # Check if it's the user's own profile
    is_own_profile = request.user.is_authenticated and (not user_id or request.user.id == user_id)
    
    # Get user's fundraisings
    user_fundraisings = None
    if profile_user:
        user_fundraisings = Fundraising.objects.filter(creator=profile_user).order_by('-created_at')
        
        # Get user's donations (excluding anonymous ones for display)
        user_donations = Donation.objects.filter(user=profile_user).order_by('-date')
        
        # Check if all user donations are anonymous (for empty state handling)
        all_anonymous = user_donations.exists() and user_donations.filter(anonymous=False).count() == 0
        
        # For display, exclude anonymous donations
        user_donations_display = user_donations.filter(anonymous=False)
    else:
        user_fundraisings = None
        user_donations_display = None
        all_anonymous = False
    
    context = {
        'profile_user': profile_user,
        'is_own_profile': is_own_profile,
        'user_fundraisings': user_fundraisings,
        'user_donations': user_donations_display,
        'all_anonymous': all_anonymous
    }
    return render(request, 'profile_page.html', context)

# Функція для оновлення статистики користувача
def update_user_statistics(user):
    try:
        # Import here to avoid circular imports
        from fundraisings.models import Fundraising, Donation
        
        # Initialize default values
        stats = {
            'created_fundraisings_count': 0,
            'completed_fundraisings_count': 0,
            'total_received_amount': 0,
            'unique_donators_count': 0,
            'supported_fundraisings_count': 0,
            'total_donated_amount': 0,
            'largest_donation_amount': 0
        }
        
        # 1. Count fundraisings created by user
        stats['created_fundraisings_count'] = Fundraising.objects.filter(creator=user).count()
        
        # 2. Count completed fundraisings if status field exists
        try:
            stats['completed_fundraisings_count'] = Fundraising.objects.filter(
                creator=user, status='completed').count()
        except Exception:
            pass
        
        # 3. Get all fundraisings created by user
        user_fundraising_ids = Fundraising.objects.filter(creator=user).values_list('id', flat=True)
        
        if user_fundraising_ids:
            # 4. Calculate total received donations and unique donors
            donations_to_user = Donation.objects.filter(fundraising_id__in=user_fundraising_ids)
            total_received = donations_to_user.aggregate(Sum('amount'))['amount__sum']
            stats['total_received_amount'] = total_received or 0
            stats['unique_donators_count'] = donations_to_user.exclude(
                user=None).values('user').distinct().count()
        
        # 5. Get user's donations
        user_donations = Donation.objects.filter(user=user)
        
        # 6. Calculate user donation stats
        stats['supported_fundraisings_count'] = user_donations.values('fundraising').distinct().count()
        total_donated = user_donations.aggregate(Sum('amount'))['amount__sum']
        stats['total_donated_amount'] = total_donated or 0
        largest_donation = user_donations.aggregate(Max('amount'))['amount__max']
        stats['largest_donation_amount'] = largest_donation or 0
        
        # Set all stats on user model
        for key, value in stats.items():
            setattr(user, key, value)
            
        # Total donations amount is the same as total_donated_amount
        user.total_donations_amount = stats['total_donated_amount']
        
        user.save()
    except Exception as e:
        print(f"Error updating user statistics: {e}")

# Функція для редагування профілю
@login_required(login_url='/login/')
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль успішно оновлено!')
            return redirect('profile_page')
    else:
        form = ProfileUpdateForm(instance=request.user)
    
    return render(request, 'edit_profile.html', {'form': form, 'user': request.user})

def categories(request):
    user = request.user if request.user.is_authenticated else None
    return render(request, 'cats.html', {'user': user})

def about_us(request):
    user = request.user if request.user.is_authenticated else None
    return render(request, 'about_us.html', {'user': user})

def fundraisings(request):
    from fundraisings.models import Category  # Import Category model
    
    category_filter = request.GET.get('category', None)
    
    if category_filter:
        # Filter fundraisings by category
        fundraisings_list = Fundraising.objects.filter(categories__name=category_filter)
    else:
        # Show all fundraisings
        fundraisings_list = Fundraising.objects.all()
        
    # Add categories to context for the filter dropdown
    categories = Category.objects.all()
    
    context = {
        'fundraisings': fundraisings_list,
        'categories': categories,
        'user': request.user
    }
        
    return render(request, 'fundraisings.html', context)