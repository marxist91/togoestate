# core/drf_permissions.py
from rest_framework.permissions import BasePermission

class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_platform_admin()

class ListingAccessPermission(BasePermission):
    """
    Read/Write si:
    - platform admin: global
    - agency admin: agence = user.agency
    - agent: owner = user
    """
    def has_object_permission(self, request, view, obj):
        user = request.user
        if not user.is_authenticated:
            return False
        if user.is_platform_admin():
            return True
        if user.is_agency_admin() and obj.agency_id == user.agency_id:
            return True
        if user.is_agent() and obj.owner_id == user.id:
            return True
        return False

    def has_permission(self, request, view):
        # pour les listes, on autorise si au moins agent
        user = request.user
        return user.is_authenticated and (user.is_platform_admin() or user.is_agency_admin() or user.is_agent())