from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class UserAdminFormTests(TestCase):
    def setUp(self):
        # Créer un superuser pour accéder à l’admin
        self.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123"
        )
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_add_user_form_contains_role_and_agency(self):
        """
        Vérifie que le formulaire d’ajout utilisateur dans l’admin
        contient bien les champs 'role' et 'agency'.
        """
        url = reverse("admin:accounts_user_add")
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        html = response.content.decode()

        # Vérifie la présence des champs
        self.assertIn('name="role"', html, "Le champ 'role' est absent du formulaire admin")
        self.assertIn('name="agency"', html, "Le champ 'agency' est absent du formulaire admin")