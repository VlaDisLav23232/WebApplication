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

# Define a view function for the home page
def home(request):
    return render(request, 'index.html')

# Define a view function for the login page
def login_page(request):
    # Якщо користувач вже авторизований, перенаправляємо на головну
    if request.user.is_authenticated:
        return redirect('/home/')
        
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not CustomUser.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Неправильне ім\'я користувача')
            return redirect('/login/')
        
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Неправильний пароль")
            return redirect('/login/')
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('/home/')
    
    # Render the login page template (GET request)
    return render(request, 'signin.html')

# Define a view function for the registration page
def register_page(request):
    # Якщо користувач вже авторизований, перенаправляємо на головну
    if request.user.is_authenticated:
        return redirect('/home/')
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            # Автоматично авторизуємо користувача
            login(request, user)
            return redirect('/home/')  # Перенаправляємо на головну сторінку
    else:
        form = RegisterForm()
    
    return render(request, 'signup.html', {'form': form})

# Функція для виходу з облікового запису
def logout_view(request):
    logout(request)
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

# Оновлена функція profile_page
@login_required(login_url='/login/')
def profile_page(request):
    user = request.user
    context = {
        'user': user
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

def fundraisings(request):
    return render(request, 'fundraisings.html')

def categories(request):
    return render(request, 'cats.html')

def about_us(request):
    return render(request, 'about_us.html')