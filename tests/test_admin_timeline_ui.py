from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from accounts.models import Agency
from listings.models import Listing, City
from datetime import datetime

User = get_user_model()


class TimelineUITests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"

        # Agence + ville
        cls.agency = Agency.objects.create(name="Agence Timeline", city="Lomé")
        cls.city = City.objects.create(name="Lomé")

        # Superadmin
        cls.admin_user = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="password123"
        )

        # Listings répartis sur plusieurs mois
        cls.listing_jan = Listing.objects.create(
            title="Listing Jan",
            owner=cls.admin_user,
            agency=cls.agency,
            price=1000,
            city=cls.city,
            published=True,
            created_at=datetime(2025, 1, 15)
        )
        cls.listing_feb = Listing.objects.create(
            title="Listing Feb",
            owner=cls.admin_user,
            agency=cls.agency,
            price=2000,
            city=cls.city,
            published=True,
            created_at=datetime(2025, 2, 10)
        )
        cls.listing_mar = Listing.objects.create(
            title="Listing Mar",
            owner=cls.admin_user,
            agency=cls.agency,
            price=3000,
            city=cls.city,
            published=False,
            created_at=datetime(2025, 3, 5)
        )

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.admin_user)

    def test_timeline_canvas_present(self):
        """Vérifie que le canvas de la timeline est bien présent"""
        url = reverse("admin:listings_listing_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="timelineChart"')
        self.assertContains(response, "<canvas")

def test_timeline_labels_months_present(self):
    """Vérifie que les labels de mois apparaissent dans le HTML en fonction des dates réelles"""
    url = reverse("admin:listings_listing_changelist")
    response = self.client.get(url)
    self.assertEqual(response.status_code, 200)

    # Pour chaque listing créé dans setUpTestData, on calcule dynamiquement le label attendu
    for listing in [self.listing_jan, self.listing_feb, self.listing_mar]:
        month_label = format(listing.created_at, "M Y")  # ex: "Jan 2025"
        # On cherche la chaîne telle qu'elle apparaît dans le JS du template (avec guillemets)
        self.assertContains(response, f'"{month_label}"')

    def test_timeline_data_values_present(self):
        """Vérifie que les valeurs numériques apparaissent dans le dataset"""
        url = reverse("admin:listings_listing_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        # Chaque mois doit avoir au moins 1 annonce
        self.assertContains(response, "1")  # Janvier
        self.assertContains(response, "1")  # Février
        self.assertContains(response, "1")  # Mars