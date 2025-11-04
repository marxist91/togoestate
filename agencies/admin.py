from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib import admin

from .models import Agency, Region, District, City
from .filters import RegionListFilter, DistrictListFilter, CityListFilter

# 👉 Import de ton admin_site cockpit centralisé
from core.admin_site import admin_site


@admin.register(Agency, site=admin_site)
class AgencyAdmin(admin.ModelAdmin):
    list_display = (
        "name", "city", "get_district", "get_region",
        "email", "phone", "verified_badge", "created_at", "users_link",
    )
    list_filter = ("verified", RegionListFilter, DistrictListFilter, CityListFilter, "created_at")
    search_fields = ("name", "city__name", "city__district__name", "city__district__region__name")
    ordering = ("name",)
    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    prepopulated_fields = {"slug": ("name",)}

    # === Helpers visuels ===
    def verified_badge(self, obj):
        color = "#16a34a" if obj.verified else "#ef4444"
        label = _("Vérifiée") if obj.verified else _("Non vérifiée")
        return format_html(
            '<span style="padding:2px 8px;border-radius:12px;font-weight:600;color:white;background:{};">{}</span>',
            color, label,
        )
    verified_badge.short_description = _("Statut")
    verified_badge.admin_order_field = "verified"

    def users_link(self, obj):
        # ⚠️ Important : utiliser le namespace cockpit_admin
        url = reverse("cockpit_admin:accounts_user_changelist") + f"?agency__id__exact={obj.id}"
        count = getattr(obj, "users", None).count() if hasattr(obj, "users") else 0
        return format_html('<a href="{}">{}</a>', url, _("{count} utilisateur(s)").format(count=count))
    users_link.short_description = _("Utilisateurs")

    def get_district(self, obj):
        return obj.city.district.name if obj.city else None
    get_district.short_description = _("District")

    def get_region(self, obj):
        return obj.city.district.region.name if obj.city else None
    get_region.short_description = _("Région")

    # === Permissions cockpit ===
    def _call_or_bool(self, obj, attr_name):
        """Helper pour appeler une méthode booléenne ou lire un attribut."""
        attr = getattr(obj, attr_name, None)
        return attr() if callable(attr) else bool(attr)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if self._call_or_bool(user, "is_platform_admin"):
            return qs
        if self._call_or_bool(user, "is_agency_admin"):
            return qs.filter(pk=user.agency_id)
        return qs.none()

    def has_view_permission(self, request, obj=None):
        user = request.user
        if self._call_or_bool(user, "is_platform_admin"):
            return True
        if self._call_or_bool(user, "is_agency_admin"):
            return obj is None or obj.pk == user.agency_id
        return False

    def has_change_permission(self, request, obj=None):
        user = request.user
        if self._call_or_bool(user, "is_platform_admin"):
            return True
        if self._call_or_bool(user, "is_agency_admin"):
            return obj is None or obj.pk == user.agency_id
        return False

    def has_delete_permission(self, request, obj=None):
        user = request.user
        if self._call_or_bool(user, "is_platform_admin"):
            return True
        return False  # admin agence ne peut pas supprimer son agence

    def has_add_permission(self, request):
        return self._call_or_bool(request.user, "is_platform_admin")


# 👉 Enregistre aussi Region, District, City dans cockpit_admin
@admin.register(Region, site=admin_site)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)


@admin.register(District, site=admin_site)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ("name", "region")
    list_filter = ("region",)
    search_fields = ("name", "region__name")


@admin.register(City, site=admin_site)
class CityAdmin(admin.ModelAdmin):
    list_display = ("name", "district", "get_region")
    list_filter = ("district__region", "district")
    search_fields = ("name", "district__name", "district__region__name")

    def get_region(self, obj):
        return obj.district.region
    get_region.short_description = "Région"