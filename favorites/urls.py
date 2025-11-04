from django.urls import path
from . import views

app_name = 'favorites'

urlpatterns = [
    path('toggle/<int:listing_id>/', views.toggle_favorite, name='toggle_favorite'),
    path('list/', views.favorites_list, name='favorites_list'),
]
