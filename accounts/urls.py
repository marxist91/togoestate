from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),

    # Dashboard générique (redirige selon rôle)
    path("dashboard/", views.dashboard, name="dashboard"),

    # Dashboards spécifiques
    path("dashboard/platform/", views.dashboard, name="dashboard_platform"),
    path("dashboard/agency/<int:agency_id>/", views.dashboard_agence, name="dashboard_agency"),
    path("dashboard/customer/", views.dashboard, name="dashboard_customer"),

    # Gestion agences (Platform Admin uniquement)
    path("agencies/", views.agency_list, name="agency_list"),
    path("agencies/create/", views.agency_create, name="agency_create"),
    path("agencies/<slug:slug>/verify/", views.agency_verify, name="agency_verify"),

    # Demande d’agence
    path("agency/request/", views.agency_request, name="agency_request"),

    # Gestion des agents d'agence
    path("agency/<int:agency_id>/agents/", views.agency_agents, name="agency_agents"),
    path("agency/<int:agency_id>/statistics/", views.agency_statistics, name="agency_statistics"),

    # Gestion des rendez-vous
    path("appointments/", views.appointments_list, name="appointments_list"),
    path("appointments/<int:appointment_id>/", views.appointment_detail, name="appointment_detail"),
    path("appointments/create/<int:listing_id>/", views.appointment_create, name="appointment_create"),
    path("appointments/<int:appointment_id>/status/<str:status>/", views.appointment_update_status, name="appointment_update_status"),
]