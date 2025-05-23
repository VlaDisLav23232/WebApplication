"""
Authentication forms for the Dovir Web Application.

This module provides forms for user registration and profile updates,
including validation logic for fields like passwords, dates, and contact information.
"""

import re
from datetime import date, timedelta
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser

COUNTRIES = [
    "Австралія", "Австрія", "Азербайджан", "Албанія", "Алжир", "Ангола", "Аргентина", "Афганістан", 
    "Бангладеш", "Бельгія", "Білорусь", "Болгарія", "Бразилія", "Велика Британія", "Вірменія", 
    "Греція", "Грузія", "Данія", "Естонія", "Єгипет",
    "Ізраїль", "Індія", "Ірландія", "Іспанія", 
    "Італія", "Казахстан", "Канада", "Китай",
    "Кіпр", "Латвія", "Литва", "Ліхтенштейн", "Люксембург", 
    "Македонія", "Малайзія", "Мальта", "Марокко", "Мексика", "Молдова", "Монако", "Нідерланди", 
    "Німеччина", "Норвегія", "Об'єднані Арабські Емірати",
    "Польща", "Португалія", "Росія", "Румунія", 
    "Сербія", "Сінгапур", "Словаччина", "Словенія", "США", "Туреччина", "Угорщина", "Україна", 
    "Фінляндія", "Франція", "Хорватія", "Чехія", "Швейцарія", "Швеція", "Японія"
]

COUNTRY_CHOICES = [(country, country) for country in COUNTRIES]

class RegisterForm(forms.ModelForm):
    """
    Form for user registration.
    
    Handles validation of user input for account creation including password rules,
    name formatting, and age requirements.
    """
    password = forms.CharField(widget=forms.PasswordInput())
    confirm_password = forms.CharField(widget=forms.PasswordInput())
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, required=True)
    phone = forms.CharField(max_length=15, required=True)

    class Meta:
        """
        Meta class for RegisterForm.
        """
        model = CustomUser
        fields = ['email', 'first_name', 'last_name', 'birth_date', 'country', 'phone', 'password']

    def clean_first_name(self):
        """
        Validate first name - must contain only letters and apostrophes.
        
        Returns:
            str: Validated first name
        """
        first_name = self.cleaned_data.get('first_name')
        if not re.match(r'^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\']+$', first_name):
            raise ValidationError("Ім'я має містити лише літери та апостроф")
        return first_name

    def clean_last_name(self):
        """
        Validate last name - must contain only letters and apostrophes.
        
        Returns:
            str: Validated last name
        """
        last_name = self.cleaned_data.get('last_name')
        if not re.match(r'^[a-zA-Zа-яА-ЯіІїЇєЄґҐ\']+$', last_name):
            raise ValidationError("Прізвище має містити лише літери та апостроф")
        return last_name

    def clean_email(self):
        """
        Validate email - must be unique in the system.
        
        Returns:
            str: Validated email
        """
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Користувач з такою електронною поштою вже існує")
        return email

    def clean_phone(self):
        """
        Validate phone - must be unique in the system.
        
        Returns:
            str: Validated phone number
        """
        phone = self.cleaned_data.get('phone')
        if CustomUser.objects.filter(phone=phone).exists():
            raise ValidationError("Користувач з таким номером телефону вже існує")
        return phone

    def clean_password(self):
        """
        Validate password - must meet complexity requirements.
        
        Returns:
            str: Validated password
        """
        password = self.cleaned_data.get("password")
        if len(password) < 8:
            raise ValidationError("Пароль має бути не менше 8 символів")
        if not any(c.isupper() for c in password):
            raise ValidationError("Пароль повинен містити хоча б одну велику літеру")
        if not re.search(r'[0-9]', password):
            raise ValidationError("Пароль повинен містити хоча б одну цифру")
        return password

    def clean_birth_date(self):
        """
        Validate birth date - user must be at least 14 years old.
        
        Returns:
            date: Validated birth date
        """
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        min_birth_date = today - timedelta(days=365 * 14)  # 14 years ago

        if birth_date and birth_date > min_birth_date:
            raise ValidationError("Вам має бути не менше 14 років для реєстрації")

        return birth_date

    def clean(self):
        """
        Cross-field validation to ensure passwords match.
        
        Returns:
            dict: Cleaned form data
        """
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            raise ValidationError("Паролі не співпадають")
        return cleaned_data


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for updating user profile information.
    
    Handles validation for profile fields including date formatting.
    """
    birth_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)

    class Meta:
        """
        Meta class for ProfileUpdateForm.
        """
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'bio', 'birth_date',
                  'country', 'region', 'city', 'address', 'phone',
                  'avatar', 'instagram', 'facebook', 'telegram']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4}),
        }

    def clean_birth_date(self):
        """
        Validate birth date - user must be at least 14 years old.
        
        Returns:
            date: Validated birth date
        """
        birth_date = self.cleaned_data.get('birth_date')
        today = date.today()
        min_birth_date = today - timedelta(days=365 * 14)  # 14 years ago

        if birth_date and birth_date > min_birth_date:
            raise ValidationError("Вам має бути не менше 14 років")

        return birth_date
