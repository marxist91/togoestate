from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Agency
from listings.models import Listing, City

User = get_user_model()


class AuditReportTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"

        # Création d'une agence et d'une ville
        cls.agency = Agency.objects.create(name="Agence Audit", city="Lomé")
        cls.city = City.objects.create(name="Lomé")

        # Création d'un superadmin pour accéder à l'admin
        cls.admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="password123"
        )

        # Création d'un agent
        cls.agent = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="password123",
            role=User.Roles.AGENT,
            agency=cls.agency,
            is_staff=True,
        )

        # Listings (dont un volontairement sans district pour tester l’audit)
        cls.listing1 = Listing.objects.create(
            title="Listing 1",
            owner=cls.agent,
            agency=cls.agency,
            price=1000,
            city=cls.city,
            district=None,  # 👈 manquant
        )
        cls.listing2 = Listing.objects.create(
            title="Listing 2",
            owner=cls.agent,
            agency=cls.agency,
            price=2000,
            city=cls.city,
            district=None,  # 👈 manquant
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_audit_report_json(self):
        """Vérifie que l’endpoint JSON renvoie les stats d’audit attendues"""
        url = reverse(f"{self.namespace}:audit-report")
        response = self.client.get(url, HTTP_X_REQUESTED_WITH="XMLHttpRequest")  # simulate AJAX
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Vérifie les clés attendues par ton endpoint réel
        self.assertIn("audit", data)
        self.assertIn("total_annonces", data)
        self.assertIn("missing_city_count", data)
        self.assertIn("missing_district_count", data)

        # Vérifie les valeurs
        self.assertEqual(data["audit"], "listings")
        self.assertEqual(data["total_annonces"], Listing.objects.count())
        self.assertEqual(data["missing_city_count"], 0)
        self.assertEqual(data["missing_district_count"], 2)

    def test_audit_report_template(self):
        """Vérifie que la vue template affiche bien le titre et les stats"""
        url = reverse(f"{self.namespace}:audit-report")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        html = response.content.decode()

        # Vérifie que le titre attendu apparaît
        self.assertIn("Audit qualité des données", html)

        # Vérifie que les stats apparaissent dans le HTML
        self.assertIn(str(Listing.objects.count()), html)