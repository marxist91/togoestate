# ...existing code...
from django.contrib import admin
from .models import Listing, ListingPhoto

class ListingPhotoInline(admin.TabularInline):
    model = ListingPhoto
    extra = 1

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'agency', 'owner', 'category', 'listing_type', 'price', 'city', 'published', 'created_at')
    list_filter = ('agency', 'category', 'listing_type', 'published', 'city')
    search_fields = ('title', 'city', 'agency__name', 'owner__username')
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ListingPhotoInline]

    def _call_or_bool(self, obj, attr_name):
        attr = getattr(obj, attr_name, None)
        return attr() if callable(attr) else bool(attr)
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if user.is_platform_admin():
            return qs
        if user.is_agency_admin():
            return qs.filter(agency=user.agency)
        if user.is_agent():
            return qs.filter(owner=user)
        return qs.none()

    
"""    def get_queryset(self, request):
        qs = super().get_queryset(request)
        user = request.user
        if self._call_or_bool(user, 'is_platform_admin'):
            return qs
        if self._call_or_bool(user, 'is_agency_admin'):
            return qs.filter(agency_id=getattr(user, 'agency_id', None))
        if self._call_or_bool(user, 'is_agent'):
            return qs.filter(owner_id=user.id)
        return qs.none()
  """

def save_model(self, request, obj, form, change):
        user = request.user
        if not self._call_or_bool(user, 'is_platform_admin'):
            if hasattr(user, 'agency'):
                obj.agency = user.agency
            if not getattr(obj, 'owner_id', None):
                obj.owner = user
        super().save_model(request, obj, form, change)

@admin.register(ListingPhoto)
class ListingPhotoAdmin(admin.ModelAdmin):
    list_display = ('listing', 'image_url', 'is_cover', 'order')
# ...existing code...