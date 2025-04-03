# Import necessary modules and models
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *

# Define a view function for the home page
def home(request):
    return render(request, 'fundraisings.html')

# Define a view function for the login page
def login_page(request):
    # Check if the HTTP request method is POST (form submission)
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Check if a user with the provided username exists
        if not User.objects.filter(username=username).exists():
            # Display an error message if the username does not exist
            messages.error(request, 'Invalid Username')
            return redirect('/login/')
        
        # Authenticate the user with the provided username and password
        user = authenticate(username=username, password=password)
        
        if user is None:
            # Display an error message if authentication fails (invalid password)
            messages.error(request, "Invalid Password")
            return redirect('/login/')
        else:
            # Log in the user and redirect to the home page upon successful login
            login(request, user)
            return redirect('/home/')
    
    # Render the login page template (GET request)
    return render(request, 'signin.html')

# Define a view function for the registration page
def register_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')  # Отримуємо email
        phone = request.POST.get('phone')  # Отримуємо телефон
        password = request.POST.get('password')

        # Перевірка наявності користувача з таким же username, email або телефоном
        if User.objects.filter(username=username).exists():
            messages.info(request, "Username already taken!")
            return redirect('/register/')

        if User.objects.filter(email=email).exists():
            messages.info(request, "Email already in use!")
            return redirect('/register/')

        # Перевіряємо телефон (якщо він є в моделі користувача)
        if User.objects.filter(userprofile__phone=phone).exists():
            messages.info(request, "Phone number already in use!")
            return redirect('/register/')

        # Створення користувача
        user = User.objects.create_user(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save()

        # Збереження телефону, якщо у моделі є `UserProfile`
        user.userprofile.phone = phone
        user.userprofile.save()
        
        print("Account created successfully!")
        messages.info(request, "Account created successfully!")
        return redirect('/register/')

    return render(request, 'signup.html')


def profile_page(request):
    return render(request, 'profile_page.html')

def fundraisings(request):
    return render(request, 'fundraisings.html')

def categories(request):
    return render(request, 'cats.html')