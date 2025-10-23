from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin
from django.urls import path, reverse
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect
from django.db.models import Count

from .models import Listing, ListingPhoto, Agency
from django.contrib.auth import get_user_model
from django.db.models.functions import TruncMonth

# Import de ton CustomUserAdmin défini dans accounts/admin.py
from accounts.admin import CustomUserAdmin

User = get_user_model()


# === Admin cockpit personnalisé ===
class AuditAdminSite(admin.AdminSite):
    site_header = "Cockpit Admin"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("mes-annonces/", self.admin_view(self.mes_annonces), name="mes-annonces"),
            path("audit-report/", self.admin_view(self.audit_report), name="audit-report"),
        ]
        return custom_urls + urls

    def mes_annonces(self, request):
        # Redirige vers la liste des annonces (ListingAdmin changelist)
        url = reverse("cockpit_admin:listings_listing_changelist", current_app=self.name)
        return redirect(url)

    def audit_report(self, request):
        total = Listing.objects.count()
        missing_city = Listing.objects.filter(city__isnull=True).values("id")
        missing_district = Listing.objects.filter(district__isnull=True).values("id")

        report = {
            "audit": "listings",
            "total_annonces": total,
            "missing_city_count": missing_city.count(),
            "missing_district_count": missing_district.count(),
            "missing_city_ids": [obj["id"] for obj in missing_city],
            "missing_district_ids": [obj["id"] for obj in missing_district],
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(report)

        context = dict(
            self.each_context(request),
            title="Audit qualité des données",
            report=report,
        )
        return TemplateResponse(request, "admin/audit_report.html", context)


# Remplace l’admin par défaut
admin_site = AuditAdminSite(name="cockpit_admin")


# === Inline pour photos ===
class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1


# === Admin Listing ===
@admin.register(Listing, site=admin_site)
class ListingAdmin(admin.ModelAdmin):
    change_list_template = "admin/listings/listing/change_list.html"  # 👈 pour injecter tes liens custom
    list_display = (
        "title", "agency", "owner", "category", "listing_type",
        "price", "city", "published", "created_at"
    )
    list_filter = ("agency", "category", "listing_type", "published", "city")
    search_fields = ("title", "city__name", "agency__name", "owner__username")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingPhotoInline]
    
    def changelist_view(self, request, extra_context=None):
        qs = self.get_queryset(request)
        stats = {
            "total": qs.count(),
            "published": qs.filter(published=True).count(),
            "unpublished": qs.filter(published=False).count(),
        }
        
                # Stats par agence (nom + nombre d'annonces)
        agency_stats = (
            qs.values("agency__name")
              .annotate(total=Count("id"))
              .order_by("agency__name")
        )
        
        # Timeline par mois (création)
        timeline_stats = (
            qs.annotate(month=TruncMonth("created_at"))
              .values("month")
              .annotate(total=Count("id"))
              .order_by("month")
        )



        extra_context = extra_context or {}
        extra_context["stats"] = stats
        extra_context["agency_stats"] = list(agency_stats)
        extra_context["timeline_stats"] = list(timeline_stats)


        return super().changelist_view(request, extra_context=extra_context)


    def _call_or_bool(self, obj, attr_name):
        attr = getattr(obj, attr_name, None)
        return attr() if callable(attr) else bool(attr)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if self._call_or_bool(user, "is_platform_admin"):
            return qs
        if self._call_or_bool(user, "is_agency_admin"):
            return qs.filter(agency=user.agency)
        if self._call_or_bool(user, "is_agent"):
            return qs.filter(owner=user)
        return qs.none()

    def save_model(self, request, obj, form, change):
        user = request.user
        if not self._call_or_bool(user, "is_platform_admin"):
            if hasattr(user, "agency"):
                obj.agency = user.agency
            if not getattr(obj, "owner_id", None):
                obj.owner = user
        super().save_model(request, obj, form, change)


# === Admin ListingPhoto ===
@admin.register(ListingPhoto, site=admin_site)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ("listing", "image_url", "is_cover", "order")


# === Admin Agency ===
@admin.register(Agency, site=admin_site)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at",)
    list_filter = ("created_at",)
    search_fields = ("name", "address", "email")
    ordering = ("-created_at",)

    def change_view(self, request, object_id, form_url="", extra_context=None):
        agency = self.get_object(request, object_id)

        # Stats liées à l’agence
        users_count = agency.users.count()
        listings_total = agency.listings.count()
        listings_published = agency.listings.filter(published=True).count()
        listings_unpublished = listings_total - listings_published

        stats = {
            "users_count": users_count,
            "listings_total": listings_total,
            "listings_published": listings_published,
            "listings_unpublished": listings_unpublished,
        }

        extra_context = extra_context or {}
        extra_context["stats"] = stats

        return super().change_view(request, object_id, form_url, extra_context=extra_context)


# === Nettoyage et réenregistrement ===
try:
    admin_site.unregister(User)
except admin.sites.NotRegistered:
    pass

try:
    admin_site.unregister(Group)
except admin.sites.NotRegistered:
    pass

# Réenregistre User avec ton CustomUserAdmin
admin_site.register(User, CustomUserAdmin)

# Réenregistre Group avec GroupAdmin
admin_site.register(Group, GroupAdmin)