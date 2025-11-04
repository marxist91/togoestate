from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from agencies.models import Agency

User = get_user_model()

class Command(BaseCommand):
    help = "Reset complet de la base de dev/test + onboarding cockpit-ready"

    def add_arguments(self, parser):
        parser.add_argument("--superuser", type=str, default="root", help="Nom du superuser")
        parser.add_argument("--superpass", type=str, default="root123", help="Mot de passe du superuser")
        parser.add_argument("--agency", type=str, default="Agence Demo", help="Nom de l'agence")
        parser.add_argument("--admin", type=str, default="admin_demo", help="Nom d'utilisateur de l'admin")
        parser.add_argument("--adminpass", type=str, default="admin123", help="Mot de passe de l'admin")
        parser.add_argument("--agents", type=int, default=2, help="Nombre d'agents à créer")

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️ Reset complet de la base en cours..."))

        # 1. Flush la base (drop toutes les données)
        call_command("flush", interactive=False)

        # 2. Rejoue toutes les migrations
        call_command("migrate")

        # 3. Crée un superuser
        if not User.objects.filter(username=options["superuser"]).exists():
            User.objects.create_superuser(
                username=options["superuser"],
                password=options["superpass"],
                email="admin@example.com"
            )
            self.stdout.write(self.style.SUCCESS(f"Superuser '{options['superuser']}' créé (mdp: {options['superpass']})"))
        else:
            self.stdout.write(self.style.WARNING(f"Superuser '{options['superuser']}' existe déjà"))

        # 4. Crée une agence
        agency, _ = Agency.objects.get_or_create(name=options["agency"])
        self.stdout.write(self.style.SUCCESS(f"Agence '{agency.name}' prête"))

        # 5. Crée un agency_admin
        if not User.objects.filter(username=options["admin"]).exists():
            admin = User.objects.create_user(
                username=options["admin"],
                password=options["adminpass"],
                agency=agency,
                roles=["agency_admin"],
            )
            self.stdout.write(self.style.SUCCESS(f"Agency admin '{options['admin']}' créé (mdp: {options['adminpass']})"))
        else:
            admin = User.objects.get(username=options["admin"])
            self.stdout.write(self.style.WARNING(f"Agency admin '{options['admin']}' existe déjà"))

        # 6. Crée des agents
        for i in range(options["agents"]):
            username = f"agent_demo{i+1}"
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password="agent123",
                    agency=agency,
                    roles=["agent"],
                )
                self.stdout.write(self.style.SUCCESS(f"Agent '{username}' créé (mdp: agent123)"))
            else:
                self.stdout.write(self.style.WARNING(f"Agent '{username}' existe déjà"))

        self.stdout.write(self.style.SUCCESS("🚀 Reset complet terminé, base prête pour dev/test !"))