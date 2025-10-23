from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = "Audit cockpit-ready : liste toutes les annonces sans city ou district"

    def handle(self, *args, **options):
        missing_city = Listing.objects.filter(city__isnull=True)
        missing_district = Listing.objects.filter(district__isnull=True)

        total = Listing.objects.count()
        self.stdout.write(self.style.NOTICE(f"=== AUDIT LISTINGS COCKPIT-READY ==="))
        self.stdout.write(self.style.NOTICE(f"Total annonces : {total}"))

        # Annonces sans ville
        if missing_city.exists():
            self.stdout.write(self.style.WARNING(
                f"\nAnnonces sans city ({missing_city.count()}) :"
            ))
            for listing in missing_city[:20]:  # limite affichage
                self.stdout.write(f" - ID {listing.id} | titre: {listing}")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Toutes les annonces ont une ville."))

        # Annonces sans quartier
        if missing_district.exists():
            self.stdout.write(self.style.WARNING(
                f"\nAnnonces sans district ({missing_district.count()}) :"
            ))
            for listing in missing_district[:20]:
                self.stdout.write(f" - ID {listing.id} | titre: {listing}")
        else:
            self.stdout.write(self.style.SUCCESS("\n✅ Toutes les annonces ont un quartier."))

        self.stdout.write(self.style.NOTICE("\n=== FIN AUDIT ==="))