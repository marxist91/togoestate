# agencies/management/commands/create_agency_with_admin.py
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from agencies.models import Agency

User = get_user_model()


class Command(BaseCommand):
    help = "Crée une agence avec un agency_admin et quelques agents pour les tests"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, default="Agence Demo", help="Nom de l'agence")
        parser.add_argument("--admin", type=str, default="admin_demo", help="Nom d'utilisateur de l'admin")
        parser.add_argument("--password", type=str, default="admin123", help="Mot de passe de l'admin")
        parser.add_argument("--agents", type=int, default=2, help="Nombre d'agents à créer")

    def handle(self, *args, **options):
        name = options["name"]
        admin_username = options["admin"]
        password = options["password"]
        nb_agents = options["agents"]

        # Créer l'agence
        agency, created = Agency.objects.get_or_create(name=name)
        if created:
            self.stdout.write(self.style.SUCCESS(f"Agence '{name}' créée"))
        else:
            self.stdout.write(self.style.WARNING(f"Agence '{name}' existe déjà"))

        # Créer l'admin
        if not User.objects.filter(username=admin_username).exists():
            admin = User.objects.create_user(
                username=admin_username,
                password=password,
                agency=agency,
                role="agency_admin",   # si tu as un champ role
                roles=["agency_admin"] # si tu as un champ roles JSON
            )
            self.stdout.write(self.style.SUCCESS(f"Admin '{admin_username}' créé avec mot de passe '{password}'"))
        else:
            admin = User.objects.get(username=admin_username)
            self.stdout.write(self.style.WARNING(f"Admin '{admin_username}' existe déjà"))

        # Créer les agents
        for i in range(nb_agents):
            username = f"agent_demo{i+1}"
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password="agent123",
                    agency=agency,
                    role="agent",
                    roles=["agent"]
                )
                self.stdout.write(self.style.SUCCESS(f"Agent '{username}' créé (mdp: agent123)"))
            else:
                self.stdout.write(self.style.WARNING(f"Agent '{username}' existe déjà"))

        self.stdout.write(self.style.SUCCESS("Onboarding terminé 🚀"))