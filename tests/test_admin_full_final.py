from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib import admin
from django.urls import reverse
from accounts.models import Agency
from accounts.admin import CustomUserAdmin

User = get_user_model()

class UserAdminFullFinalTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Créer une agence pour tester l'attribution
        cls.agency = Agency.objects.create(name="Test Agency", city="Lomé")

        # Créer un superuser pour accéder à l’admin
        cls.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123"
        )

        # Créer un utilisateur normal pour tester la modification
        cls.normal_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="password123",
            role=User.Roles.AGENT,
            agency=cls.agency
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_user_admin_is_custom(self):
        """Vérifie que User est bien enregistré avec CustomUserAdmin"""
        self.assertIn(User, admin.site._registry, "❌ Le modèle User n'est pas enregistré dans l'admin")
        user_admin_class = admin.site._registry[User].__class__
        self.assertEqual(
            user_admin_class,
            CustomUserAdmin,
            f"❌ Mauvais UserAdmin actif : {user_admin_class.__name__} au lieu de CustomUserAdmin"
        )

    def test_add_user_form_contains_role_and_agency(self):
        """Vérifie que le formulaire d’ajout utilisateur contient role et agency"""
        url = reverse("admin:accounts_user_add")
        response = self.client.get(url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="role"', html, "❌ Le champ 'role' est absent du formulaire d’ajout")
        self.assertIn('name="agency"', html, "❌ Le champ 'agency' est absent du formulaire d’ajout")

    def test_change_user_form_contains_role_and_agency(self):
        """Vérifie que le formulaire de modification utilisateur contient role et agency"""
        url = reverse("admin:accounts_user_change", args=[self.normal_user.pk])
        response = self.client.get(url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn('name="role"', html, "❌ Le champ 'role' est absent du formulaire de modification")
        self.assertIn('name="agency"', html, "❌ Le champ 'agency' est absent du formulaire de modification")

    def test_user_list_display_contains_role_and_agency(self):
        """Vérifie que la liste des utilisateurs affiche les colonnes role et agency"""
        url = reverse("admin:accounts_user_changelist")
        response = self.client.get(url)
        html = response.content.decode()

        self.assertEqual(response.status_code, 200)
        self.assertIn("Role", html, "❌ La colonne 'Role' est absente de la liste des utilisateurs")
        self.assertIn("Agency", html, "❌ La colonne 'Agency' est absente de la liste des utilisateurs")