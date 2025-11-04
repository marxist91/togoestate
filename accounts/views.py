from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .forms import SignUpForm, LoginForm, AgencyCreateForm
from .models import User, Agency, Appointment
from listings.models import Listing
from saved_searches.models import SavedSearch
from favorites.models import Favorite
from django.utils import timezone


# === Helpers de rôle ===
def is_platform_admin(user):
    return user.is_authenticated and user.is_platform_admin()

def is_agency_admin(user):
    return user.is_authenticated and (user.is_agency_admin() or user.is_platform_admin())


# === Authentification ===
def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Compte créé avec succès. Vous pouvez vous connecter.")
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


# === Demande d'agence ===
def agency_request(request):
    if request.method == 'POST':
        form = AgencyCreateForm(request.POST)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.verified = False  # en attente de validation
            agency.save()
            messages.success(request, "Votre demande d'agence a été envoyée. Elle sera validée par un administrateur.")
            return redirect('index')
    else:
        form = AgencyCreateForm()
    return render(request, 'accounts/agency_request.html', {'form': form})


# === Dashboard Agence ===
@login_required
def dashboard_agence(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    agency_users = User.objects.filter(agency=agency)
    listings = Listing.objects.filter(agency=agency)

    stats = {
        "total": listings.count(),
        "published": listings.filter(published=True).count(),
        "draft": listings.filter(published=False).count(),
        "agents": agency_users.count(),
    }

    context = {
        "agency": agency,
        "agency_users": agency_users,
        "listings": listings,
        "stats": stats,
    }
    return render(request, "accounts/dashboard_agency.html", context)


# === Dashboard générique cockpit-ready ===
@login_required
def dashboard(request):
    user = request.user

    # Platform Admin
    if user.is_platform_admin():
        agencies_count = Agency.objects.count()
        users_count = User.objects.count()
        return render(request, 'accounts/dashboard_admin_platform.html', {
            'agencies_count': agencies_count,
            'users_count': users_count,
        })

    # Agency Admin ou Agent
    elif user.is_agency_admin() or user.is_agent():
        agency = user.agency
        agency_users = User.objects.filter(agency=agency)
        listings = Listing.objects.filter(agency=agency)
        stats = {
            "total": listings.count(),
            "published": listings.filter(published=True).count(),
            "draft": listings.filter(published=False).count(),
            "agents": agency_users.count(),
        }
        return render(request, 'accounts/dashboard_agency.html', {
            'agency': agency,
            'agency_users': agency_users,
            'listings': listings,
            'stats': stats,
        })

    # Client simple
    else:
        recent_listings = Listing.objects.filter(published=True).prefetch_related('photos').order_by('-created_at')[:6]
        favorites = Favorite.objects.filter(user=user).select_related('listing')
        saved_searches = SavedSearch.objects.filter(user=user)
        return render(request, 'accounts/dashboard_customer.html', {
            "recent_listings": recent_listings,
            "favorites": favorites,
            "saved_searches": saved_searches,
        })


# === Gestion des agences (Platform Admin uniquement) ===
@user_passes_test(is_platform_admin)
def agency_create(request):
    if request.method == 'POST':
        form = AgencyCreateForm(request.POST)
        if form.is_valid():
            agency = form.save()
            messages.success(request, f"Agence '{agency.name}' créée.")
            return redirect('agency_list')
    else:
        form = AgencyCreateForm()
    return render(request, 'accounts/agency_form.html', {'form': form})


@user_passes_test(is_platform_admin)
def agency_list(request):
    agencies = Agency.objects.all()
    return render(request, 'accounts/agency_list.html', {'agencies': agencies})


@user_passes_test(is_platform_admin)
def agency_verify(request, slug):
    agency = get_object_or_404(Agency, slug=slug)
    agency.verified = True
    agency.save()
    messages.success(request, f"Agence '{agency.name}' vérifiée.")
    return redirect('agency_list')


# === Liste des agents d'une agence (Agency Admin uniquement) ===
@login_required
def agency_agents(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    # Vérifier que l'utilisateur est admin de cette agence
    if not (request.user.is_agency_admin() and request.user.agency == agency):
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    agency_users = User.objects.filter(agency=agency).order_by('username')

    context = {
        "agency": agency,
        "agency_users": agency_users,
    }
    return render(request, "accounts/agency_agents.html", context)


# === Statistiques d'une agence (Agency Admin uniquement) ===
@login_required
def agency_statistics(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    # Vérifier que l'utilisateur est admin de cette agence
    if not (request.user.is_agency_admin() and request.user.agency == agency):
        messages.error(request, "Accès non autorisé.")
        return redirect('dashboard')

    listings = Listing.objects.filter(agency=agency)
    total_listings = listings.count()
    published_listings = listings.filter(published=True).count()
    draft_listings = listings.filter(published=False).count()

    if total_listings > 0:
        publication_rate = round((published_listings / total_listings) * 100)
    else:
        publication_rate = 0

    context = {
        "agency": agency,
        "total_listings": total_listings,
        "published_listings": published_listings,
        "draft_listings": draft_listings,
        "publication_rate": publication_rate,
    }
    return render(request, "accounts/agency_statistics.html", context)


# === Gestion des rendez-vous ===

@login_required
def appointments_list(request):
    """Liste des rendez-vous pour l'utilisateur connecté"""
    user = request.user

    if user.is_agent():
        # Agent voit ses rendez-vous
        appointments = Appointment.objects.filter(agent=user).select_related('listing', 'customer')
    elif user.is_customer():
        # Client voit ses rendez-vous
        appointments = Appointment.objects.filter(customer=user).select_related('listing', 'agent')
    else:
        # Admin voit tous les rendez-vous de son agence
        appointments = Appointment.objects.filter(
            listing__agency=user.agency
        ).select_related('listing', 'agent', 'customer')

    # Statistiques
    stats = {
        'total': appointments.count(),
        'pending': appointments.filter(status='pending').count(),
        'confirmed': appointments.filter(status='confirmed').count(),
        'completed': appointments.filter(status='completed').count(),
        'cancelled': appointments.filter(status='cancelled').count(),
    }

    context = {
        'appointments': appointments,
        'stats': stats,
    }
    return render(request, 'accounts/appointments_list.html', context)


@login_required
def appointment_detail(request, appointment_id):
    """Détail d'un rendez-vous"""
    appointment = get_object_or_404(
        Appointment.objects.select_related('listing', 'agent', 'customer'),
        id=appointment_id
    )

    # Vérifier les permissions
    user = request.user
    if not (
        user == appointment.agent or
        user == appointment.customer or
        (user.is_agency_admin() and user.agency == appointment.listing.agency)
    ):
        messages.error(request, "Accès non autorisé.")
        return redirect('appointments_list')

    context = {
        'appointment': appointment,
    }
    return render(request, 'accounts/appointment_detail.html', context)


@login_required
def appointment_create(request, listing_id):
    """Créer un rendez-vous pour une annonce"""
    listing = get_object_or_404(Listing, id=listing_id, published=True)
    user = request.user

    # Vérifier que l'utilisateur est un client
    if not user.is_customer():
        messages.error(request, "Seuls les clients peuvent prendre rendez-vous.")
        return redirect('listing_detail', slug=listing.slug)

    if request.method == 'POST':
        # Ici on utiliserait un formulaire, mais pour simplifier on crée directement
        scheduled_date_str = request.POST.get('scheduled_date')
        notes = request.POST.get('notes', '')

        try:
            from django.utils.dateparse import parse_datetime
            scheduled_date = parse_datetime(scheduled_date_str)
            if not scheduled_date:
                raise ValueError("Date invalide")

            # Trouver un agent disponible pour cette annonce
            agent = User.objects.filter(
                agency=listing.agency,
                role='agent'
            ).first()

            if not agent:
                messages.error(request, "Aucun agent disponible pour cette annonce.")
                return redirect('listing_detail', slug=listing.slug)

            # Créer le rendez-vous
            appointment = Appointment.objects.create(
                listing=listing,
                agent=agent,
                customer=user,
                scheduled_date=scheduled_date,
                notes=notes,
                status='pending'
            )

            messages.success(request, "Votre demande de rendez-vous a été envoyée.")
            return redirect('appointment_detail', appointment_id=appointment.id)

        except Exception as e:
            messages.error(request, f"Erreur lors de la création du rendez-vous: {str(e)}")

    context = {
        'listing': listing,
    }
    return render(request, 'accounts/appointment_create.html', context)


@login_required
def appointment_update_status(request, appointment_id, status):
    """Mettre à jour le statut d'un rendez-vous"""
    appointment = get_object_or_404(Appointment, id=appointment_id)
    user = request.user

    # Vérifier les permissions
    if not (
        user == appointment.agent or
        (user.is_agency_admin() and user.agency == appointment.listing.agency)
    ):
        messages.error(request, "Accès non autorisé.")
        return redirect('appointments_list')

    # Vérifier que le statut est valide
    valid_statuses = ['pending', 'confirmed', 'cancelled', 'completed']
    if status not in valid_statuses:
        messages.error(request, "Statut invalide.")
        return redirect('appointment_detail', appointment_id=appointment.id)

    # Vérifier que le rendez-vous peut être modifié
    if not appointment.can_be_modified:
        messages.error(request, "Ce rendez-vous ne peut plus être modifié.")
        return redirect('appointment_detail', appointment_id=appointment.id)

    appointment.status = status
    appointment.save()

    status_messages = {
        'confirmed': "Rendez-vous confirmé.",
        'cancelled': "Rendez-vous annulé.",
        'completed': "Rendez-vous marqué comme terminé.",
    }

    messages.success(request, status_messages.get(status, "Statut mis à jour."))
    return redirect('appointment_detail', appointment_id=appointment.id)
