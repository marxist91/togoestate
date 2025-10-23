from django.urls import path, include
from . import views



urlpatterns = [
    path('', views.listing_list, name='listing_list'),
    path('manage/', views.manage_listings, name='manage_listings'),
    
    path('<slug:slug>/', views.listing_detail, name='listing_detail'),


]