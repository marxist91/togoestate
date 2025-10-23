from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class CockpitUXLinksTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"
        cls.admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="password123"
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_mes_annonces_link_visible_in_listing_changelist(self):
        """Vérifie que le lien 'mes-annonces/' apparaît dans la page ListingAdmin"""
        url = reverse(f"{self.namespace}:listings_listing_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()

        mes_annonces_url = reverse(f"{self.namespace}:mes-annonces")
        self.assertIn(mes_annonces_url, html)

    def test_audit_report_link_visible_in_listing_changelist(self):
        """Vérifie que le lien 'audit-report/' apparaît dans la page ListingAdmin"""
        url = reverse(f"{self.namespace}:listings_listing_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()

        audit_url = reverse(f"{self.namespace}:audit-report")
        self.assertIn(audit_url, html)