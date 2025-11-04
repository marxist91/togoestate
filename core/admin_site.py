from django.contrib import admin
from django.urls import path, reverse
from django.http import JsonResponse
from django.template.response import TemplateResponse
from django.shortcuts import redirect

from listings.models import Listing


class AuditAdminSite(admin.AdminSite):
    """Admin cockpit centralisé pour tout le projet."""
    site_header = "Cockpit Admin"
    site_title = "Cockpit Admin"
    index_title = "Tableau de bord cockpit"

    def get_urls(self):
        """Ajoute des URLs custom cockpit (audit, raccourcis, etc.)."""
        urls = super().get_urls()
        custom_urls = [
            path("mes-annonces/", self.admin_view(self.mes_annonces), name="mes-annonces"),
            path("audit-report/", self.admin_view(self.audit_report), name="audit-report"),
        ]
        return custom_urls + urls

    def mes_annonces(self, request):
        """Redirige vers la liste des annonces cockpit."""
        url = reverse("cockpit_admin:listings_listing_changelist", current_app=self.name)
        return redirect(url)

    def audit_report(self, request):
        """Rapport qualité des données sur les listings."""
        total = Listing.objects.count()
        missing_city = Listing.objects.filter(city__isnull=True).values("id")

        report = {
            "audit": "listings",
            "total_annonces": total,
            "missing_city_count": missing_city.count(),
            "missing_city_ids": [obj["id"] for obj in missing_city],
        }

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse(report)

        context = dict(
            self.each_context(request),
            title="Audit qualité des données",
            report=report,
        )
        return TemplateResponse(request, "admin/audit_report.html", context)


# 👉 Instance unique cockpit_admin utilisée partout
admin_site = AuditAdminSite(name="cockpit_admin")
