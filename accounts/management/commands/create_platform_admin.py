from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Crée un superuser cockpit‑ready (platform admin) avec username/email/mot de passe passés en arguments"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Nom d'utilisateur du superuser")
        parser.add_argument("email", type=str, help="Email du superuser")
        parser.add_argument("password", type=str, help="Mot de passe du superuser")

    def handle(self, *args, **options):
        username = options["username"]
        email = options["email"]
        password = options["password"]

        if User.objects.filter(username=username).exists():
            self.stderr.write(self.style.ERROR(f"Un utilisateur '{username}' existe déjà"))
            return

        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )

        self.stdout.write(self.style.SUCCESS(
            f"Superuser cockpit‑ready '{username}' créé avec succès (email: {email})"
        ))
        
        #python manage.py create_platform_admin marcel admin@example.com marcel2025