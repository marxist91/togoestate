from django.contrib.auth.management import create_permissions
from django.apps import apps
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.db import transaction

User = get_user_model()

# 1) Régénérer toutes les permissions
for app_config in apps.get_app_configs():
    create_permissions(app_config, verbosity=0)

# 2) Récupérer les permissions add/change sur Listing
add_perm = Permission.objects.get(content_type__app_label="listings", codename="add_listing")
change_perm = Permission.objects.get(content_type__app_label="listings", codename="change_listing")

# 3) Donner ces droits à tous les users liés à une agence
with transaction.atomic():
    qs = User.objects.exclude(agency__isnull=True)
    updated = 0
    for user in qs:
        user.is_staff = True
        user.user_permissions.add(add_perm, change_perm)
        user.save(update_fields=["is_staff"])
        updated += 1

print(f"Utilisateurs mis à jour : {updated}")