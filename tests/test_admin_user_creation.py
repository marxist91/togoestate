from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Agency

User = get_user_model()


class UserAdminCreationTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"  # cohérent avec ton AuditAdminSite
        cls.app_label = User._meta.app_label
        cls.model_name = User._meta.model_name

        # Crée une agence pour lier l'utilisateur
        cls.agency = Agency.objects.create(name="Test Agency", city="Lomé")

        # Crée un superuser pour accéder à l’admin
        cls.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_create_user_with_role_and_agency(self):
        """Vérifie qu’un utilisateur créé via l’admin cockpit persiste bien role et agency"""
        url = reverse(f"{self.namespace}:{self.app_label}_{self.model_name}_add")

        post_data = {
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "role": User.Roles.AGENT,   # 👈 rôle choisi
            "agency": self.agency.pk,  # 👈 agence choisie
            "is_active": "on",
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200, "❌ La requête POST n’a pas abouti correctement")

        # Vérifie que l’utilisateur a bien été créé
        self.assertTrue(User.objects.filter(username="newuser").exists(), "❌ L’utilisateur n’a pas été créé")
        user = User.objects.get(username="newuser")

        # Vérifie la persistance des champs
        self.assertEqual(user.role, User.Roles.AGENT, "❌ Le rôle n’a pas été sauvegardé correctement")
        self.assertEqual(user.agency, self.agency, "❌ L’agence n’a pas été sauvegardée correctement")