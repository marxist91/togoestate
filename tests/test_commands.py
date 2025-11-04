from django.core.management import call_command
from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.models import Agency

User = get_user_model()


class CommandTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.agency = Agency.objects.create(name="Agence Horizon", city="Lomé")

    def test_create_agency_admin(self):
        call_command(
            "create_agency_admin",
            "admin_agence",
            "admin_agence@example.com",
            "pass123",
            str(self.agency.id),
        )
        user = User.objects.get(username="admin_agence")
        self.assertEqual(user.role, "agency_admin")
        self.assertTrue(user.is_staff)
        self.assertEqual(user.agency, self.agency)

    def test_create_agent(self):
        call_command(
            "create_agent",
            "agent1",
            "agent1@example.com",
            "pass456",
            str(self.agency.id),
        )
        user = User.objects.get(username="agent1")
        self.assertEqual(user.role, "agent")
        self.assertTrue(user.is_staff)
        self.assertEqual(user.agency, self.agency)

    def test_create_customer(self):
        call_command(
            "create_customer",
            "client1",
            "client1@example.com",
            "pass789",
        )
        user = User.objects.get(username="client1")
        self.assertEqual(user.role, "customer")
        self.assertFalse(user.is_staff)
        self.assertIsNone(user.agency)  # un customer n’est pas rattaché à une agence