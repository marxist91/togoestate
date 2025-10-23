import json
from django.core.management.base import BaseCommand
from listings.models import Listing

class Command(BaseCommand):
    help = "Audit cockpit-ready (JSON) : génère un rapport JSON des annonces sans city ou district"

    def add_arguments(self, parser):
        parser.add_argument(
            "--pretty",
            action="store_true",
            help="Affiche le JSON avec indentation pour lecture humaine",
        )

    def handle(self, *args, **options):
        total = Listing.objects.count()
        missing_city = Listing.objects.filter(city__isnull=True).values("id")
        missing_district = Listing.objects.filter(district__isnull=True).values("id")

        report = {
            "audit": "listings",
            "total_annonces": total,
            "missing_city_count": missing_city.count(),
            "missing_district_count": missing_district.count(),
            "missing_city_ids": [obj["id"] for obj in missing_city],
            "missing_district_ids": [obj["id"] for obj in missing_district],
        }

        if options["pretty"]:
            self.stdout.write(json.dumps(report, indent=4, ensure_ascii=False))
        else:
            self.stdout.write(json.dumps(report, ensure_ascii=False))