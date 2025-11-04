from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.forms.models import BaseInlineFormSet
from adminsortable2.admin import SortableAdminBase, SortableInlineAdminMixin, CustomInlineFormSetMixin

from .models import Listing, ListingPhoto
from django.contrib.auth import get_user_model
from core.admin_site import admin_site

# 👉 Import des filtres hiérarchiques
from agencies.filters import RegionListFilter, DistrictListFilter, CityListFilter

User = get_user_model()


# === Inline avec aperçu et validation is_cover ===
class ListingPhotoInlineFormset(CustomInlineFormSetMixin, BaseInlineFormSet):
    def __init__(self, *args, **kwargs):
        # Remove arguments not accepted by BaseFormSet in Django 5.2
        kwargs.pop('default_order_direction', None)
        kwargs.pop('default_order_field', None)
        super().__init__(*args, **kwargs)
        # Set the default order field manually for Django 5.2 compatibility
        if not hasattr(self, 'default_order_field') or self.default_order_field is None:
            self.default_order_field = 'order'
        if not hasattr(self, 'default_order_direction'):
            self.default_order_direction = 0

    def clean(self):
        super().clean()
        cover_count = 0
        for form in self.forms:
            if not hasattr(form, "cleaned_data"):
                continue
            if form.cleaned_data.get("DELETE"):
                continue
            if form.cleaned_data.get("is_cover"):
                cover_count += 1
        if cover_count > 1:
            raise ValidationError("Une seule photo peut être définie comme couverture.")


class ListingPhotoInline(SortableInlineAdminMixin, admin.StackedInline):
    model = ListingPhoto
    extra = 1
    formset = ListingPhotoInlineFormset
    fields = ("image", "preview", "is_cover", "order")
    readonly_fields = ("preview",)

    def preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height:120px; border:1px solid #ccc;"/>',
                obj.image.url,
            )
        return "—"
    preview.short_description = "Aperçu"

    def has_add_permission(self, request, obj=None):
        """Tous peuvent ajouter des photos à leurs annonces"""
        return True

    def has_change_permission(self, request, obj=None):
        """Tous peuvent modifier les photos de leurs annonces"""
        return True

    def has_delete_permission(self, request, obj=None):
        """Tous peuvent supprimer les photos de leurs annonces"""
        return True


# === Admin Listing cockpit‑ready ===
@admin.register(Listing, site=admin_site)
class ListingAdmin(SortableAdminBase, admin.ModelAdmin):
    list_display = (
        "title", "agency", "owner", "category", "listing_type",
        "price", "city", "get_district", "get_region",
        "published", "created_at"
    )
    list_filter = (
        "agency", "category", "listing_type", "published",
        RegionListFilter, DistrictListFilter, CityListFilter
    )
    search_fields = (
        "title", "city__name", "city__district__name",
        "city__district__region__name", "agency__name", "owner__username"
    )
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingPhotoInline]

    # Helpers cockpit-ready
    def get_district(self, obj):
        return obj.city.district if obj.city else None
    get_district.short_description = "District"
    get_district.admin_order_field = "city__district__name"

    def get_region(self, obj):
        return obj.city.district.region if obj.city else None
    get_region.short_description = "Région"
    get_region.admin_order_field = "city__district__region__name"

    # === Helper pour vérifier permissions ===
    def _call_or_bool(self, obj, attr_name):
        attr = getattr(obj, attr_name, None)
        return attr() if callable(attr) else bool(attr)

    # === QuerySet filtré selon le rôle ===
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        
        # Superuser / Platform Admin = tout voir
        if self._call_or_bool(user, "is_platform_admin"):
            return qs
        
        # Agency Admin = voir toute son agence
        if self._call_or_bool(user, "is_agency_admin"):
            return qs.filter(agency=user.agency)
        
        # Agent = voir toute son agence
        if self._call_or_bool(user, "is_agent"):
            return qs.filter(agency=user.agency)
        
        return qs.none()

    # === Permissions : Tous peuvent créer ===
    def has_add_permission(self, request):
        """Platform Admin, Agency Admin et Agent peuvent créer"""
        return (
            self._call_or_bool(request.user, "is_platform_admin")
            or self._call_or_bool(request.user, "is_agency_admin")
            or self._call_or_bool(request.user, "is_agent")
        )

    def has_change_permission(self, request, obj=None):
        """
        - Platform Admin = tout modifier
        - Agency Admin = modifier toute son agence
        - Agent = modifier uniquement SES annonces
        """
        user = request.user
        
        # Platform Admin = tout modifier
        if self._call_or_bool(user, "is_platform_admin"):
            return True
        
        # Agency Admin = modifier toute son agence
        if self._call_or_bool(user, "is_agency_admin"):
            return obj is None or obj.agency == user.agency
        
        # Agent = modifier uniquement ses propres annonces
        if self._call_or_bool(user, "is_agent"):
            return obj is None or obj.owner == user
        
        return False

    def has_delete_permission(self, request, obj=None):
        """
        - Platform Admin = tout supprimer
        - Agency Admin = supprimer toute son agence
        - Agent = supprimer uniquement SES annonces
        """
        user = request.user
        
        # Platform Admin = tout supprimer
        if self._call_or_bool(user, "is_platform_admin"):
            return True
        
        # Agency Admin = supprimer toute son agence
        if self._call_or_bool(user, "is_agency_admin"):
            return obj is None or obj.agency == user.agency
        
        # Agent = supprimer uniquement ses propres annonces
        if self._call_or_bool(user, "is_agent"):
            return obj is None or obj.owner == user
        
        return False

    # === Readonly fields : agents ne peuvent pas changer agency/owner ===
    def get_readonly_fields(self, request, obj=None):
        """Agents ne peuvent pas modifier agency et owner"""
        user = request.user
        readonly = list(self.readonly_fields)
        
        # Agent = agency et owner en readonly
        if self._call_or_bool(user, "is_agent"):
            if "agency" not in readonly:
                readonly.append("agency")
            if "owner" not in readonly:
                readonly.append("owner")
        
        return readonly

    # === Form : masquer agency/owner pour non-superusers ===
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        user = request.user
        
        # Seul Platform Admin voit agency/owner
        if not self._call_or_bool(user, "is_platform_admin"):
            form.base_fields.pop("agency", None)
            form.base_fields.pop("owner", None)
        
        return form

    # === Valeurs par défaut selon le rôle ===
    def get_changeform_initial_data(self, request):
        data = super().get_changeform_initial_data(request)
        user = request.user
        
        # Agency Admin = pré-remplir son agence et lui comme owner
        if self._call_or_bool(user, "is_agency_admin"):
            data["agency"] = user.agency_id
            data["owner"] = user.id
        
        # Agent = pré-remplir son agence et lui comme owner
        if self._call_or_bool(user, "is_agent"):
            data["agency"] = user.agency_id
            data["owner"] = user.id
        
        return data

    # === Sauvegarde avec assignation auto ===
    def save_model(self, request, obj, form, change):
        user = request.user
        
        # Création : assigner automatiquement agency et owner
        if not obj.pk:
            if not obj.owner_id:
                obj.owner = user
            if not obj.agency_id and hasattr(user, "agency"):
                obj.agency = user.agency
        
        super().save_model(request, obj, form, change)


# === Admin ListingPhoto ===
@admin.register(ListingPhoto, site=admin_site)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ("listing", "image", "is_cover", "order")
    list_filter = ("is_cover", "listing__agency")
    search_fields = ("listing__title",)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        
        # Platform Admin = tout voir
        if self._call_or_bool(user, "is_platform_admin"):
            return qs
        
        # Agency Admin = voir son agence
        if self._call_or_bool(user, "is_agency_admin"):
            return qs.filter(listing__agency=user.agency)
        
        # Agent = voir son agence
        if self._call_or_bool(user, "is_agent"):
            return qs.filter(listing__agency=user.agency)
        
        return qs.none()
    
    def has_change_permission(self, request, obj=None):
        """Agent peut modifier les photos de ses annonces"""
        user = request.user
        
        if self._call_or_bool(user, "is_platform_admin"):
            return True
        
        if self._call_or_bool(user, "is_agency_admin"):
            return obj is None or obj.listing.agency == user.agency
        
        if self._call_or_bool(user, "is_agent"):
            return obj is None or obj.listing.owner == user
        
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Agent peut supprimer les photos de ses annonces"""
        return self.has_change_permission(request, obj)
    
    def _call_or_bool(self, obj, attr_name):
        attr = getattr(obj, attr_name, None)
        return attr() if callable(attr) else bool(attr)


# === Nettoyage et réenregistrement ===
try:
    admin_site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin_site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Réenregistre Group avec GroupAdmin
admin_site.register(Group, GroupAdmin)