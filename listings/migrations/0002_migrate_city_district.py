from django.db import migrations

def migrate_city_and_district(apps, schema_editor):
    Listing = apps.get_model("listings", "Listing")
    City = apps.get_model("locations", "City")
    District = apps.get_model("locations", "District")

    for listing in Listing.objects.all():
        # Migration de la ville
        if getattr(listing, "old_city", None):
            city_name = listing.old_city.strip().title()
            if city_name:
                city, _ = City.objects.get_or_create(name=city_name)
                listing.city = city

        # Migration du quartier
        if getattr(listing, "old_district", None):
            district_name = listing.old_district.strip().title()
            if district_name and listing.city:
                district, _ = District.objects.get_or_create(
                    name=district_name,
                    city=listing.city
                )
                listing.district = district

        listing.save(update_fields=["city", "district"])

def reverse_migration(apps, schema_editor):
    Listing = apps.get_model("listings", "Listing")
    for listing in Listing.objects.all():
        if listing.city:
            listing.old_city = listing.city.name
        if listing.district:
            listing.old_district = listing.district.name
        listing.save(update_fields=["old_city", "old_district"])

class Migration(migrations.Migration):

    dependencies = [
        ("locations", "0001_initial"),
        ("listings", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(migrate_city_and_district, reverse_migration),
    ]