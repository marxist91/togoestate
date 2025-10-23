from django.core.management.base import BaseCommand
from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = "Diagnostic : liste les champs exposés par le UserAdmin actif (fieldsets et add_fieldsets)"

    def handle(self, *args, **options):
        # Récupérer le UserAdmin actuellement enregistré
        if User not in admin.site._registry:
            self.stdout.write(self.style.ERROR("❌ Aucun UserAdmin trouvé dans admin.site._registry"))
            return

        user_admin = admin.site._registry[User]

        self.stdout.write(self.style.SUCCESS("✅ UserAdmin actif trouvé :"))
        self.stdout.write(f"   Classe : {user_admin.__class__.__name__}")

        # Champs affichés dans fieldsets (formulaire de modification)
        self.stdout.write("\n📋 Champs dans fieldsets (édition) :")
        for name, opts in user_admin.fieldsets:
            fields = opts.get("fields", [])
            self.stdout.write(f" - {name}: {fields}")

        # Champs affichés dans add_fieldsets (formulaire de création)
        self.stdout.write("\n📋 Champs dans add_fieldsets (création) :")
        for name, opts in getattr(user_admin, "add_fieldsets", []):
            fields = opts.get("fields", [])
            self.stdout.write(f" - {name}: {fields}")

        # Champs affichés dans list_display
        self.stdout.write("\n📋 Champs dans list_display (liste) :")
        self.stdout.write(f" - {user_admin.list_display}")