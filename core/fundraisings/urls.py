from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_fundraising, name='create_fundraising'),
    path('<int:pk>/', views.donate, name='donate'),
    path('<int:pk>/update/', views.update_fundraising, name='update_fundraising'),
    path('<int:pk>/delete/', views.delete_fundraising, name='delete_fundraising'),
    path('<int:pk>/update-donation/', views.update_donation, name='update_donation'),
]
