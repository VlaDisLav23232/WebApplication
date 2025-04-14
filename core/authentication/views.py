#Changed by claude



# Import necessary modules and models
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from .forms import RegisterForm
from django.urls import reverse
from django import forms
import re
from fundraisings.models import Fundraising

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
    # If no user_id is provided, show the current user's profile
    if user_id is None:
        profile_user = request.user
    else:
        # Get the user with the specified ID or return 404 if not found
        profile_user = get_object_or_404(CustomUser, id=user_id)
    
    # Check if the profile being viewed is the current user's profile
    is_own_profile = (profile_user.id == request.user.id)
    
    context = {
        'profile_user': profile_user,  # The user whose profile is being viewed
        'user': request.user,          # The currently logged-in user
        'is_own_profile': is_own_profile
    }
    
    return render(request, 'profile_page.html', context)

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