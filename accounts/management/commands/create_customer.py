from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Crée un utilisateur customer (client final, sans accès admin)"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nom d'utilisateur")
        parser.add_argument("email", type=str, help="Email")
        parser.add_argument("password", type=str, help="Mot de passe")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if User.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f"Utilisateur {username} existe déjà"))
            return

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            role="customer",   # 👈 rôle défini dans ton modèle
            is_staff=False,    # 👈 pas d'accès admin
            is_active=True,
        )

        self.stdout.write(self.style.SUCCESS(
            f"Customer '{username}' créé avec succès (sans accès admin)"
        ))