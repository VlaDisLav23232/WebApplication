"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

# Import necessary modules
from django.contrib import admin  # Django admin module
from django.urls import path, include  # URL routing and including other URL configurations
from authentication.views import *  # Import views from the authentication app
from django.conf import settings   # Application settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # Static files serving
from django.conf.urls.static import static
from fundraisings.views import *
from django.views.static import serve
import os

# Define URL patterns
urlpatterns = [
    path("", home, name="home"),
    path('home/', home, name="recipes"),      # Home page
    path('fundraisings/', fundraisings, name='fundraisings'), #fundraising page
    path('profile/', profile_page, name='profile_page'),  # Default profile (current user)
    path('profile/<int:user_id>/',\
        profile_page, name='user_profile'),  # Profile with specific user ID
    path('profile/edit/', edit_profile, name='edit_profile'),
    path("admin/", admin.site.urls),          # Admin interface
    path('login/', login_page, name='login_page'),    # Login page
    path('register/', register_page, name='register'),  # Registration page
    path('logout/', logout_view, name='logout'),  # Logout page
    path('register/categories/', categories, name='categories'), #Choose categories
    path('about_us/', about_us, name='about_us'),
    path('create_fundraising/', create_fundraising, name='create_fundraising'),
    path('fundraising/<int:pk>/', donate, name='donate'),
    path('fundraising/<int:pk>/update/', update_fundraising, name='update_fundraising'),
    path('fundraising/<int:pk>/delete/', delete_fundraising, name='delete_fundraising'),
    path('change_password/', home, name='change_password'), #change password 
    path('delete_account/', home, name='deactivate_account'),
    path('update_settings/', home, name="update_settings"),
    path('donate/<int:pk>/', donation_form, name='donation_form'),  # Donation form
    path('fundraising/', include('fundraisings.urls')),  # Include fundraisings URLs with prefix
    path('create-report/', create_report, name='create_report'),  # Create report page
    path('create-report/<int:fundraising_id>/',\
        create_report, name='create_report_with_id'),  # Create report with fundraising ID
    path('reports/', reports, name='reports'),  # Reports page
]

# Serve media files if DEBUG is True (development mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Serve static files using staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

# Updated media file serving that works in both development and production
urlpatterns += [
    path('media/<path:path>', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# Ensure that the media directory exists
os.makedirs(settings.MEDIA_ROOT, exist_ok=True)

# Simplify the media and static files configuration
# This makes the URLs work regardless of DEBUG setting
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
