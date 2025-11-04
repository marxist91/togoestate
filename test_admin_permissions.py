from django.test import RequestFactory
from django.contrib.auth import get_user_model
from listings.models import Listing
from core.admin_site import admin_site  # ton cockpit centralisé

User = get_user_model()
rf = RequestFactory()

print("=== Vérification cockpit-ready des ModelAdmin.has_*_permission et get_queryset ===")

# Récupérer les ModelAdmin enregistrés sur ton cockpit
user_admin = admin_site._registry[User]
listing_admin = admin_site._registry[Listing]

def check_permissions(label, model_admin, request):
    """Affiche les permissions avec ✅ / ⚠️"""
    add_perm = model_admin.has_add_permission(request)
    change_perm = model_admin.has_change_permission(request)
    delete_perm = model_admin.has_delete_permission(request)

    print(f"  [{label}]")
    print(f"    has_add_permission:   {'✅' if add_perm else '⚠️'} ({add_perm})")
    print(f"    has_change_permission:{'✅' if change_perm else '⚠️'} ({change_perm})")
    print(f"    has_delete_permission:{'✅' if delete_perm else '⚠️'} ({delete_perm})")

def check_queryset(label, model_admin, request, fields):
    """Affiche les objets visibles via get_queryset"""
    qs = model_admin.get_queryset(request)
    print(f"    {label} visibles:", list(qs.values_list(*fields)))

# === Vérifier les admins d’agence ===
admins = User.objects.filter(role="agency_admin", is_staff=True)
for admin_user in admins:
    request = rf.get("/")
    request.user = admin_user

    print(f"\n👑 Admin testé: {admin_user.username} (Agence: {admin_user.agency})")

    # Permissions et QS UserAdmin
    check_permissions("UserAdmin", user_admin, request)
    check_queryset("Utilisateurs", user_admin, request, ["username", "agency__name"])

    # Permissions et QS ListingAdmin
    check_permissions("ListingAdmin", listing_admin, request)
    check_queryset("Annonces", listing_admin, request, ["title", "agency__name"])

# === Vérifier les agents ===
agents = User.objects.filter(role="agent", is_staff=True)
for agent_user in agents:
    request = rf.get("/")
    request.user = agent_user

    print(f"\n👤 Agent testé: {agent_user.username} (Agence: {agent_user.agency})")

    # Permissions et QS UserAdmin
    check_permissions("UserAdmin", user_admin, request)
    check_queryset("Utilisateurs", user_admin, request, ["username", "agency__name"])

    # Permissions et QS ListingAdmin
    check_permissions("ListingAdmin", listing_admin, request)
    check_queryset("Annonces", listing_admin, request, ["title", "agency__name"])