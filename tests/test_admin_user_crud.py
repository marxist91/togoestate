from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from accounts.models import Agency
from accounts.admin import CustomUserAdmin
from django.contrib import admin

User = get_user_model()


class UserAdminCRUDTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"
        cls.app_label = User._meta.app_label
        cls.model_name = User._meta.model_name

        cls.agency1 = Agency.objects.create(name="Agence Initiale", city="Lomé")
        cls.agency2 = Agency.objects.create(name="Agence Cible", city="Kara")

        cls.admin_user = User.objects.create_superuser(
            username="admin",
            email="admin@example.com",
            password="password123"
        )

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

    # === READ ===
    def test_user_admin_is_custom(self):
        self.assertIn(User, admin.site._registry)
        user_admin_class = admin.site._registry[User].__class__
        self.assertEqual(user_admin_class, CustomUserAdmin)

    def test_user_list_display_contains_role_and_agency(self):
        url = reverse(f"{self.namespace}:{self.app_label}_{self.model_name}_changelist")
        response = self.client.get(url)
        html = response.content.decode()
        self.assertEqual(response.status_code, 200)
        self.assertIn("Role", html)
        self.assertIn("Agency", html)

    # === CREATE ===
    def test_create_user_with_role_and_agency(self):
        url = reverse(f"{self.namespace}:{self.app_label}_{self.model_name}_add")
        post_data = {
            "username": "newuser",
            "password1": "StrongPass123!",
            "password2": "StrongPass123!",
            "role": User.Roles.AGENT,
            "agency": self.agency1.pk,
            "is_active": "on",
        }
        response = self.client.post(url, post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.filter(username="newuser").exists())
        user = User.objects.get(username="newuser")
        self.assertEqual(user.role, User.Roles.AGENT)
        self.assertEqual(user.agency, self.agency1)

    # === UPDATE ===
    def test_update_user_role_and_agency(self):
        url = reverse(
            f"{self.namespace}:{self.app_label}_{self.model_name}_change",
            args=[self.normal_user.pk]
        )
        response = self.client.get(url)
        form = response.context["adminform"].form

        # Nettoyage des None → remplacés par ""
        post_data = {k: ("" if v is None else v) for k, v in form.initial.items()}

        # Ajoute les champs manquants
        for field in form.fields:
            if field not in post_data:
                post_data[field] = form.fields[field].initial or ""

        # Modifie role et agency
        post_data["role"] = User.Roles.AGENCY_ADMIN
        post_data["agency"] = self.agency2.pk

        response = self.client.post(url, post_data, follow=True)

        # Debug si formulaire invalide
        if response.context and "adminform" in response.context:
            form = response.context["adminform"].form
            if form.errors:
                print("Form errors:", form.errors)

        self.assertEqual(response.status_code, 200)

        self.normal_user.refresh_from_db()
        self.assertEqual(self.normal_user.role, User.Roles.AGENCY_ADMIN)
        self.assertEqual(self.normal_user.agency, self.agency2)

    # === DELETE ===
    def test_delete_user(self):
        url = reverse(
            f"{self.namespace}:{self.app_label}_{self.model_name}_delete",
            args=[self.normal_user.pk]
        )
        response = self.client.post(url, {"post": "yes"}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(pk=self.normal_user.pk).exists())