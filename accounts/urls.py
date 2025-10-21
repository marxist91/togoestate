from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Admin plateforme sur les agences
    path('agencies/', views.agency_list, name='agency_list'),
    path('agencies/create/', views.agency_create, name='agency_create'),
    path('agencies/<slug:slug>/verify/', views.agency_verify, name='agency_verify'),
]