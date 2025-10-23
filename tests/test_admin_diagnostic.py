from django.test import TestCase
from django.urls import reverse, NoReverseMatch
from django.contrib import admin

def get_admin_namespace():
    """
    Détecte automatiquement le namespace admin actif.
    """
    for ns in ["admin", "cockpit_admin"]:
        try:
            reverse(f"{ns}:index")
            return ns
        except NoReverseMatch:
            continue
    return None

class AdminDiagnosticTests(TestCase):
    def test_admin_namespace_and_registry(self):
        namespace = get_admin_namespace()
        print("\n=== Diagnostic AdminSite ===")
        if namespace:
            print(f"✅ Namespace actif détecté : {namespace}")
        else:
            print("❌ Aucun namespace admin valide trouvé (ni 'admin' ni 'cockpit_admin').")

        print("\n📋 Modèles enregistrés dans admin.site._registry :")
        for model, model_admin in admin.site._registry.items():
            print(f"- {model._meta.app_label}.{model.__name__} → {model_admin.__class__.__name__}")