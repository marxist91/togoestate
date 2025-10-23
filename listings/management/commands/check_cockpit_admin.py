from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from listings.admin import admin_site

User = get_user_model()

class Command(BaseCommand):
    help = "Diagnostic cockpit_admin : vérifie User, permissions et liste tous les modèles enregistrés"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            type=str,
            help="Nom d'utilisateur à tester (par défaut le premier superuser trouvé)",
        )

    def handle(self, *args, **options):
        # === Vérifier si User est enregistré ===
        if User in admin_site._registry:
            self.stdout.write(self.style.SUCCESS("✅ User est bien enregistré dans cockpit_admin"))
        else:
            self.stdout.write(self.style.ERROR("❌ User n'est PAS enregistré dans cockpit_admin"))

        # === Récupérer l'utilisateur à tester ===
        username = options.get("username")
        if username:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"❌ Utilisateur '{username}' introuvable"))
                return
        else:
            user = User.objects.filter(is_superuser=True).first()
            if not user:
                self.stdout.write(self.style.ERROR("❌ Aucun superuser trouvé, précisez --username"))
                return

        self.stdout.write(f"\n🔎 Vérification des permissions pour l'utilisateur : {user.username}")

        # === Vérifier les permissions liées au modèle User ===
        perms = ["auth.view_user", "auth.add_user", "auth.change_user", "auth.delete_user"]
        for perm in perms:
            if user.has_perm(perm):
                self.stdout.write(self.style.SUCCESS(f"   ✅ {perm}"))
            else:
                self.stdout.write(self.style.WARNING(f"   ⚠️  {perm} manquant"))

        # === Lister tous les modèles enregistrés sur cockpit_admin ===
        self.stdout.write("\n📋 Modèles enregistrés sur cockpit_admin :")
        if not admin_site._registry:
            self.stdout.write(self.style.ERROR("❌ Aucun modèle enregistré"))
        else:
            for model, model_admin in admin_site._registry.items():
                app_label = model._meta.app_label
                model_name = model._meta.model_name
                admin_class = model_admin.__class__.__name__
                self.stdout.write(f"   - {app_label}.{model_name} → {admin_class}")