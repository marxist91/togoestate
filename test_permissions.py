from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

User = get_user_model()
client = Client()

print("=== Vérification cockpit-ready des permissions ===")

admins = User.objects.filter(role="agency_admin", is_staff=True)

if not admins.exists():
    print("❌ Aucun admin d’agence trouvé.")
else:
    for admin in admins:
        client.force_login(admin)
        print(f"\nAdmin testé: {admin.username} (Agence: {admin.agency})")

        resp1 = client.get(reverse("cockpit_admin:accounts_user_add"))
        resp2 = client.get(reverse("cockpit_admin:listings_listing_add"))

        print("  Accès accounts_user_add:", resp1.status_code)
        print("  Accès listings_listing_add:", resp2.status_code)

        if resp1.status_code == 200 and resp2.status_code == 200:
            print("  ✅ Peut accéder aux formulaires d’ajout")
        else:
            print("  ⚠️ Problème de permission détecté")