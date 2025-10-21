from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Agency

@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'verified', 'created_at')
    list_filter = ('verified', 'city')
    search_fields = ('name', 'city')
    prepopulated_fields = {"slug": ("name",)}

class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Agence & Rôle', {'fields': ('agency', 'role')}),
    )
    list_display = ('username', 'email', 'role', 'agency', 'is_active', 'is_staff')
    list_filter = ('role', 'agency', 'is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'email')

admin.site.register(User, UserAdmin)