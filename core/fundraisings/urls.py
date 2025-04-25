"""URLS"""
from django.urls import path
from .views import update_fundraising
from . import views

urlpatterns = [
    path('fundraising/create/', views.create_fundraising, name='create_fundraising'),
    path('fundraising/<int:fundraising_id>/update/', views.update_fundraising, name='update_fundraising'),
    path('fundraisings/active/', views.active_fundraisings, name='active_fundraisings'),
    path('reports/', views.reports, name='reports'),
    path('create/', views.create_fundraising, name='create_fundraising'),
    path('<int:pk>/', views.donate, name='donate'),
    path('<int:pk>/update/', views.update_fundraising, name='update_fundraising'),
    path('<int:pk>/delete/', views.delete_fundraising, name='delete_fundraising'),
    path('<int:pk>/update-donation/', views.update_donation, name='update_donation'),
    path('', views.fundraisings, name='fundraisings'),
    path('create-report/', views.create_report, name='create_report'),
    path('create-report/<int:fundraising_id>/', views.create_report, name='create_report'),
]
