from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from listings.models import Listing
from agencies.models import Agency, City, District, Region  # 👈 Import from agencies

User = get_user_model()


class ListingAdminPermissionsTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.namespace = "cockpit_admin"
        cls.app_label = "listings"
        cls.model_name = "listing"

        # Créer région et district pour les villes
        cls.region = Region.objects.create(name="Maritime")
        cls.district = District.objects.create(name="Lomé", region=cls.region)

        # Deux villes
        cls.city1 = City.objects.create(name="Lomé", district=cls.district)
        cls.city2 = City.objects.create(name="Kara", district=cls.district)

        # Deux agences
        cls.agency1 = Agency.objects.create(name="Agence Alpha", city=cls.city1)
        cls.agency2 = Agency.objects.create(name="Agence Beta", city=cls.city2)

        # Permissions nécessaires
        view_perm = Permission.objects.get(codename="view_listing")

        # Utilisateurs avec is_staff=True et permission view_listing
        cls.agent1 = User.objects.create_user(
            username="agent1",
            email="agent1@example.com",
            password="password123",
            role=User.Roles.AGENT,
            agency=cls.agency1,
            is_staff=True,
        )
        cls.agent1.user_permissions.add(view_perm)

        cls.agent2 = User.objects.create_user(
            username="agent2",
            email="agent2@example.com",
            password="password123",
            role=User.Roles.AGENT,
            agency=cls.agency2,
            is_staff=True,
        )
        cls.agent2.user_permissions.add(view_perm)

        cls.agency_admin = User.objects.create_user(
            username="agencyadmin",
            email="agencyadmin@example.com",
            password="password123",
            role=User.Roles.AGENCY_ADMIN,
            agency=cls.agency1,
            is_staff=True,
        )
        cls.agency_admin.user_permissions.add(view_perm)

        cls.platform_admin = User.objects.create_superuser(
            username="superadmin",
            email="superadmin@example.com",
            password="password123",
        )

        # Listings
        cls.listing1 = Listing.objects.create(
            title="Annonce Agent1",
            owner=cls.agent1,
            agency=cls.agency1,
            price=1000,
            city=cls.city1,
        )
        cls.listing2 = Listing.objects.create(
            title="Annonce Agent2",
            owner=cls.agent2,
            agency=cls.agency2,
            price=2000,
            city=cls.city2,
        )
        cls.listing3 = Listing.objects.create(
            title="Annonce Agence1",
            owner=cls.agent1,
            agency=cls.agency1,
            price=3000,
            city=cls.city1,
        )

    def setUp(self):
        self.client = Client()

    def _get_queryset_ids(self, user):
        """Helper pour récupérer les IDs visibles dans le changelist admin"""
        self.client.force_login(user)
        url = reverse(f"{self.namespace}:{self.app_label}_{self.model_name}_changelist")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        return list(response.context["cl"].queryset.values_list("id", flat=True))

    def test_agent_sees_only_own_listings(self):
        ids = self._get_queryset_ids(self.agent1)
        self.assertIn(self.listing1.id, ids)
        self.assertIn(self.listing3.id, ids)
        self.assertNotIn(self.listing2.id, ids)

    def test_agency_admin_sees_only_agency_listings(self):
        ids = self._get_queryset_ids(self.agency_admin)
        self.assertIn(self.listing1.id, ids)
        self.assertIn(self.listing3.id, ids)
        self.assertNotIn(self.listing2.id, ids)

    def test_platform_admin_sees_all_listings(self):
        ids = self._get_queryset_ids(self.platform_admin)
        self.assertIn(self.listing1.id, ids)
        self.assertIn(self.listing2.id, ids)
        self.assertIn(self.listing3.id, ids)