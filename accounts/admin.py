from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from .models import Agency

User = get_user_model()


# === Forms customisés ===
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = (
            "username", "email", "first_name", "last_name",
            "role", "agency",   # 👈 explicitement inclus
            "is_active", "is_staff", "is_superuser",
            "groups", "user_permissions",
        )


class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email", "password1", "password2", "role", "agency")


# === Admin Agency ===
@admin.register(Agency)
class AgencyAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "verified", "created_at")
    list_filter = ("verified", "city")
    search_fields = ("name", "city")
    prepopulated_fields = {"slug": ("name",)}


# === Admin User ===
@admin.register(User)
class CustomUserAdmin(BaseUserAdmin):
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm

    list_display = (
        "username", "email", "first_name", "last_name",
        "role", "agency", "is_active", "is_staff"
    )
    list_filter = ("role", "agency", "is_staff", "is_superuser", "is_active")
    search_fields = ("username", "email")

    # Champs en lecture seule
    readonly_fields = ("last_login", "date_joined")

    # fieldsets propres (sans usable_password)
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
        ("Agence & Rôle", {"fields": ("agency", "role")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "agency"),
        }),
    )