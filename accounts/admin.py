from urllib import request
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import gettext_lazy as _
from core.admin_site import admin_site
from listings.models import Listing
from django.shortcuts import render
# from accounts.models import Favorite, SavedSearch  # Commented out as these models don't exist

User = get_user_model()

try:
    admin_site.unregister(User)
except admin.sites.NotRegistered:
    pass


# === Forms customisés ===
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "role", "agency",
            "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
        )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2", "role", "agency")


# === Admin User cockpit‑ready ===
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "username", "email", "first_name", "last_name",
        "role", "agency", "is_active", "is_staff"
    )
    list_filter = ("role", "agency", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)

    readonly_fields = ("last_login", "date_joined")

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Informations personnelles"), {"fields": ("first_name", "last_name", "email")}),
        (_("Permissions"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Dates importantes"), {"fields": ("last_login", "date_joined")}),
        (_("Agence & Rôle"), {"fields": ("agency", "role")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "agency"),
        }),
    )

    # === Helper pour vérifier les attributs/méthodes ===
    def _call_or_bool(self, obj, attr_name):
        """Helper pour appeler une méthode ou récupérer un attribut"""
        attr = getattr(obj, attr_name, None)
        return attr() if callable(attr) else bool(attr)

    # === Cockpit-ready: filtrage et permissions ===
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        
        # Superuser / Platform Admin = tout voir
        if user.is_superuser or self._call_or_bool(user, "is_platform_admin"):
            return qs
        
        # Agency Admin = voir seulement son agence
        if self._call_or_bool(user, "is_agency_admin"):
            if hasattr(user, "agency") and user.agency:
                return qs.filter(agency=user.agency)
            return qs.none()
        
        # Agent = voir seulement lui-même
        if self._call_or_bool(user, "is_agent"):
            return qs.filter(pk=user.pk)
        
        return qs.none()

    def has_add_permission(self, request):
        """Superuser et Agency Admin peuvent ajouter des utilisateurs"""
        user = request.user
        return (
            user.is_superuser
            or self._call_or_bool(user, "is_platform_admin")
            or self._call_or_bool(user, "is_agency_admin")
        )

    def has_change_permission(self, request, obj=None):
        """
        - Superuser = tout modifier
        - Agency Admin = modifier son agence
        - Agent = modifier seulement lui-même
        """
        user = request.user
        
        # Superuser / Platform Admin = tout modifier
        if user.is_superuser or self._call_or_bool(user, "is_platform_admin"):
            return True
        
        # Agency Admin = modifier son agence
        if self._call_or_bool(user, "is_agency_admin"):
            if obj is None:
                return True
            if hasattr(user, "agency") and user.agency and hasattr(obj, "agency"):
                return obj.agency == user.agency
            return False
        
        # Agent = modifier seulement lui-même
        if self._call_or_bool(user, "is_agent"):
            return obj is None or obj.pk == user.pk
        
        return False

    def has_delete_permission(self, request, obj=None):
        """
        - Superuser = tout supprimer
        - Agency Admin = supprimer son agence (sauf lui-même)
        - Agent = ne peut rien supprimer
        """
        user = request.user
        
        # Superuser / Platform Admin = tout supprimer
        if user.is_superuser or self._call_or_bool(user, "is_platform_admin"):
            return True
        
        # Agency Admin = supprimer son agence (mais pas lui-même)
        if self._call_or_bool(user, "is_agency_admin"):
            if obj is None:
                return True
            # Ne peut pas se supprimer lui-même
            if obj.pk == user.pk:
                return False
            if hasattr(user, "agency") and user.agency and hasattr(obj, "agency"):
                return obj.agency == user.agency
            return False
        
        # Agent = ne peut rien supprimer
        return False

    def get_changeform_initial_data(self, request):
        """Pré-remplir agency pour Agency Admin"""
        data = super().get_changeform_initial_data(request)
        user = request.user
        
        # Agency Admin = pré-remplir son agence
        if self._call_or_bool(user, "is_agency_admin"):
            if hasattr(user, "agency") and user.agency:
                data["agency"] = user.agency.id
        
        return data

    def save_model(self, request, obj, form, change):
        """Assigner automatiquement l'agence si non définie"""
        user = request.user
        
        # Si création par un Agency Admin et agency non définie
        if not change and self._call_or_bool(user, "is_agency_admin"):
            if not obj.agency and hasattr(user, "agency") and user.agency:
                obj.agency = user.agency
        
        super().save_model(request, obj, form, change)

    def get_form(self, request, obj=None, **kwargs):
        """Empêcher la modification de certains champs selon le rôle"""
        form = super().get_form(request, obj, **kwargs)
        user = request.user
        
        # Agency Admin = agency en readonly
        if self._call_or_bool(user, "is_agency_admin"):
            if "agency" in form.base_fields:
                form.base_fields["agency"].disabled = True
            # Ne peut pas créer de superuser
            if "is_superuser" in form.base_fields:
                form.base_fields["is_superuser"].disabled = True
        
        # Agent = la plupart des champs en readonly
        if self._call_or_bool(user, "is_agent"):
            readonly_fields = ["agency", "role", "is_staff", "is_superuser", "groups", "user_permissions"]
            for field in readonly_fields:
                if field in form.base_fields:
                    form.base_fields[field].disabled = True
        
        return form

    def get_readonly_fields(self, request, obj=None):
        """Définir les champs readonly selon le rôle"""
        readonly = list(self.readonly_fields)
        user = request.user
        
        # Agent = la plupart des champs en readonly (pour affichage)
        if self._call_or_bool(user, "is_agent"):
            readonly.extend(["agency", "role", "is_staff", "is_superuser"])
        
        return readonly
    

admin_site.register(User, CustomUserAdmin)


# === Appointment Admin ===
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('listing', 'customer', 'agent', 'scheduled_date', 'status', 'created_at')
    list_filter = ('status', 'scheduled_date', 'created_at')
    search_fields = ('listing__title', 'customer__username', 'agent__username', 'notes')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('listing', 'customer', 'agent')
        }),
        ('Détails du rendez-vous', {
            'fields': ('scheduled_date', 'duration_minutes', 'notes')
        }),
        ('Statut', {
            'fields': ('status',)
        }),
        ('Métadonnées', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        
        # Platform admin voit tout
        if user.is_superuser or user.is_platform_admin():
            return qs
        
        # Agency admin voit les rendez-vous de son agence
        if user.is_agency_admin():
            return qs.filter(listing__agency=user.agency)
        
        # Agent voit ses propres rendez-vous
        if user.is_agent():
            return qs.filter(agent=user)
        
        return qs.none()
    
    def has_change_permission(self, request, obj=None):
        if not super().has_change_permission(request, obj):
            return False
        
        user = request.user
        
        # Platform admin peut tout modifier
        if user.is_superuser or user.is_platform_admin():
            return True
        
        # Agency admin peut modifier les rendez-vous de son agence
        if user.is_agency_admin():
            if obj:
                return obj.listing.agency == user.agency
            return True
        
        # Agent peut modifier ses propres rendez-vous
        if user.is_agent():
            if obj:
                return obj.agent == user
            return True
        
        return False

admin_site.register(Appointment, AppointmentAdmin)
