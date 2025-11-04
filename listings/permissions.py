# listings/permissions.py
from rest_framework.permissions import BasePermission, SAFE_METHODS

ALLOWED_ROLES = {"agency_admin", "agent"}

class IsAgencyStaff(BasePermission):
    """
    Autorise GET pour tous, et POST/PUT/PATCH/DELETE uniquement
    pour les rôles agency_admin et agent.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        user = request.user
        if not user or not user.is_authenticated:
            return False
        # Adapte cette logique selon ton système de rôles
        user_roles = set(getattr(user, "roles", []))  # ex: user.roles = ["agent"]
        return len(ALLOWED_ROLES & user_roles) > 0

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        # Optionnel : restreindre l’édition à l’agence du user
        # Adapte selon ton modèle (ex: obj.agency == user.agency)
        try:
            return obj.can_edit(request.user)
        except Exception:
            # fallback: même règle que has_permission
            return self.has_permission(request, view)