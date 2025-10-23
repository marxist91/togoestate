from django.test import TestCase
from django.contrib import admin
from django.contrib.auth import get_user_model
from accounts.admin import CustomUserAdmin  # ta classe admin

User = get_user_model()

class UserAdminRegistryTests(TestCase):
    def test_user_admin_is_custom_and_has_role_agency(self):
        """
        Vérifie que le UserAdmin actif est bien CustomUserAdmin
        et que 'role' et 'agency' apparaissent dans ses fieldsets.
        """
        # Vérifie que User est bien enregistré dans l'admin
        self.assertIn(User, admin.site._registry, "❌ Le modèle User n'est pas enregistré dans l'admin")

        # Récupère la classe admin associée
        user_admin_instance = admin.site._registry[User]
        user_admin_class = user_admin_instance.__class__

        # Vérifie que c'est bien CustomUserAdmin
        self.assertEqual(
            user_admin_class,
            CustomUserAdmin,
            f"❌ Mauvais UserAdmin actif : {user_admin_class.__name__} au lieu de CustomUserAdmin"
        )

        # Vérifie que 'role' et 'agency' apparaissent dans les fieldsets
        all_fields = []
        for _, opts in user_admin_instance.fieldsets:
            fields = opts.get("fields", [])
            if isinstance(fields, (list, tuple)):
                all_fields.extend(fields)
            else:
                all_fields.append(fields)

        self.assertIn("role", all_fields, "❌ Le champ 'role' est absent des fieldsets de CustomUserAdmin")
        self.assertIn("agency", all_fields, "❌ Le champ 'agency' est absent des fieldsets de CustomUserAdmin")