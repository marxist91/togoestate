from django.apps import AppConfig


class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def ready(self):
        import accounts.signals
        # Import admin to register models
        import accounts.admin
        # Manually register User model with custom admin site
        from core.admin_site import admin_site
        from django.contrib.auth import get_user_model
        User = get_user_model()
        admin_site.register(User, accounts.admin.CustomUserAdmin)

