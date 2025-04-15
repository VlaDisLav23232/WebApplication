from django.urls import path
from authentication import views as auth_views

urlpatterns = [
    path('profile/<int:user_id>/', auth_views.profile_page, name='user_profile'),
    path('profile/', auth_views.profile_page, name='profile_page'),
]