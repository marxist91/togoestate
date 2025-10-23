from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Agency

User = get_user_model()


class UserAdminUpdateTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"  # cohérent avec ton AuditAdminSite
        cls.app_label = User._meta.app_label
        cls.model_name = User._meta.model_name

        # Crée deux agences pour tester le changement
        cls.agency1 = Agency.objects.create(name="Agence Initiale", city="Lomé")
        cls.agency2 = Agency.objects.create(name="Agence Cible", city="Kara")

        # Crée un superuser pour accéder à l’admin
        cls.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123"
        )

        # Crée un utilisateur normal lié à agency1
        cls.normal_user = User.objects.create_user(
            username="john",
            email="john@example.com",
            password="password123",
            role=User.Roles.AGENT,
            agency=cls.agency1
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_update_user_role_and_agency(self):
        """Vérifie qu’un utilisateur peut être modifié via l’admin cockpit (role + agency)"""
        url = reverse(
            f"{self.namespace}:{self.app_label}_{self.model_name}_change",
            args=[self.normal_user.pk]
        )

        post_data = {
            "username": self.normal_user.username,
            "email": self.normal_user.email,
            "role": User.Roles.AGENCY_ADMIN,   # 👈 nouveau rôle
            "agency": self.agency2.pk,         # 👈 nouvelle agence
            "is_active": "on",
             # Django admin exige un champ password
        }

        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200, "❌ La requête POST n’a pas abouti correctement")

        # Recharge l’utilisateur depuis la base
        self.normal_user.refresh_from_db()

        # Vérifie que les champs ont bien été mis à jour
        self.assertEqual(self.normal_user.role, User.Roles.AGENCY_ADMIN, "❌ Le rôle n’a pas été mis à jour")
        self.assertEqual(self.normal_user.agency, self.agency2, "❌ L’agence n’a pas été mise à jour")