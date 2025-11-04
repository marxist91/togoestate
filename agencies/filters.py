from django.contrib import admin
from .models import Region, District, City


class RegionListFilter(admin.SimpleListFilter):
    title = "Région"
    parameter_name = "region"

    def lookups(self, request, model_admin):
        return [(r.id, r.name) for r in Region.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__district__region_id=self.value())
        return queryset


class DistrictListFilter(admin.SimpleListFilter):
    title = "District"
    parameter_name = "district"

    def lookups(self, request, model_admin):
        return [(d.id, f"{d.name} ({d.region.name})") for d in District.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city__district_id=self.value())
        return queryset


class CityListFilter(admin.SimpleListFilter):
    title = "Ville"
    parameter_name = "city"

    def lookups(self, request, model_admin):
        return [(c.id, f"{c.name} ({c.district.name})") for c in City.objects.all()]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(city_id=self.value())
        return queryset