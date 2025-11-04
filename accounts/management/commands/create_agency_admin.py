from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import Agency

User = get_user_model()

class Command(BaseCommand):
    help = "Crée un utilisateur agency_admin rattaché à une agence"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nom d'utilisateur")
        parser.add_argument("email", type=str, help="Email")
        parser.add_argument("password", type=str, help="Mot de passe")
        parser.add_argument("agency_id", type=int, help="ID de l'agence")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]
        agency_id = options["agency_id"]

        try:
            agency = Agency.objects.get(id=agency_id)
        except Agency.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Agence avec ID {agency_id} introuvable"))
            return

        if User.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f"Utilisateur {username} existe déjà"))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="agency_admin",   # 👈 rôle défini dans ton modèle
            agency=agency,
            is_staff=True,         # 👈 nécessaire pour accéder à l’admin
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f"Agency admin '{username}' créé avec succès pour l'agence '{agency.name}'"
        ))