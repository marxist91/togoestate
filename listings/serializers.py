from rest_framework import serializers
from .models import Listing


class ListingWriteSerializer(serializers.ModelSerializer):
    """
    Serializer utilisé pour la création et la mise à jour des annonces.
    On limite aux champs éditables par l’utilisateur.
    """
    class Meta:
        model = Listing
        fields = [
            "title", "slug", "price", "currency", "city", "category",
            "listing_type", "surface", "bedrooms", "bathrooms",
            "address", "district", "description", "published",
        ]


class ListingReadSerializer(serializers.ModelSerializer):
    """
    Serializer utilisé pour la lecture (API GET).
    Inclut les helpers cover_photo() et gallery_photos().
    """
    cover_photo = serializers.SerializerMethodField()
    gallery_photos = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            "id", "title", "slug", "price", "currency",
            "city", "category", "listing_type",
            "surface", "bedrooms", "bathrooms",
            "address", "district", "description", "published",
            "cover_photo", "gallery_photos",
        ]

    def get_cover_photo(self, obj):
        return obj.cover_photo()

    def get_gallery_photos(self, obj):
        return [p.image.url for p in obj.gallery_photos() if p.image]


# ✅ Alias pour compatibilité avec les imports existants
ListingSerializer = ListingReadSerializer