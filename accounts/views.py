from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import SignUpForm, LoginForm, AgencyCreateForm
from .models import User, Agency

def is_platform_admin(user):
    return user.is_authenticated and user.is_platform_admin()

def is_agency_admin(user):
    return user.is_authenticated and (user.is_agency_admin() or user.is_platform_admin())

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

def agency_request(request):
    if request.method == 'POST':
        form = AgencyCreateForm(request.POST)
        if form.is_valid():
            agency = form.save(commit=False)
            agency.verified = False  # en attente
            agency.save()
            messages.success(request, "Votre demande d'agence a été envoyée. Elle sera validée par un administrateur.")
            return redirect('index')
    else:
        form = AgencyCreateForm()
    return render(request, 'accounts/agency_request.html', {'form': form})



def dashboard_agence(request, agency_id):
    agency = get_object_or_404(Agency, id=agency_id)

    # Récupérer les utilisateurs liés à l’agence
    equipe = agency.users.all()  # si related_name="users"

    # Stats annonces
    listings_total = agency.listings.count()
    listings_published = agency.listings.filter(published=True).count()

    context = {
        "agency": agency,
        "equipe": equipe,
        "listings_total": listings_total,
        "listings_published": listings_published,
    }
    return render(request, "dashboard_agence.html", context)




@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def dashboard(request):
    # Vue générique de dashboard selon le rôle
    if request.user.is_platform_admin():
        agencies_count = Agency.objects.count()
        users_count = User.objects.count()
        return render(request, 'accounts/dashboard_admin_platform.html', {
            'agencies_count': agencies_count,
            'users_count': users_count,
        })
    elif request.user.is_agency_admin() or request.user.is_agent():
        agency = request.user.agency
        agency_users = User.objects.filter(agency=agency)
        return render(request, 'accounts/dashboard_agency.html', {
            'agency': agency,
            'agency_users': agency_users,
        })
    else:
        return render(request, 'accounts/dashboard_customer.html')

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