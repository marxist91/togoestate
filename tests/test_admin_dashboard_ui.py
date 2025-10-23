from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Agency
from listings.models import Listing, City

User = get_user_model()


class AuditReportUITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"

        # Agence + ville
        cls.agency = Agency.objects.create(name="Agence Test", city="Lomé")
        cls.city = City.objects.create(name="Lomé")

        # Superadmin
        cls.admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="password123"
        )

        # Listings (1 complet, 1 sans district)
        cls.listing1 = Listing.objects.create(
            title="Listing 1",
            owner=cls.admin_user,
            agency=cls.agency,
            price=1000,
            city=cls.city,
            published=True,
        )
        cls.listing2 = Listing.objects.create(
            title="Listing 2",
            owner=cls.admin_user,
            agency=cls.agency,
            price=2000,
            city=cls.city,
            published=False,
            district=None,  # volontairement incomplet
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_audit_report_contains_labels(self):
        """Vérifie que les libellés principaux apparaissent dans le template"""
        url = reverse(f"{self.namespace}:audit-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, "Audit qualité des données")
        self.assertContains(response, "Total annonces")
        self.assertContains(response, "Missing city count")
        self.assertContains(response, "Missing district count")

    def test_audit_report_contains_numeric_values(self):
        """Vérifie que les valeurs numériques calculées apparaissent"""
        url = reverse(f"{self.namespace}:audit-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        total = Listing.objects.count()
        missing_city = Listing.objects.filter(city__isnull=True).count()
        missing_district = Listing.objects.filter(district__isnull=True).count()

        self.assertContains(response, str(total))
        self.assertContains(response, str(missing_city))
        self.assertContains(response, str(missing_district))

    def test_audit_report_contains_graph_canvas(self):
        """Vérifie que le graphique Chart.js est bien présent"""
        url = reverse(f"{self.namespace}:audit-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        self.assertContains(response, 'id="chart-container"')
        self.assertContains(response, "<canvas")