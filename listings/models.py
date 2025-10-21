from django.db import models
from django.utils.text import slugify
from accounts.models import Agency ,User


class Listing(models.Model):
    class ListingType(models.TextChoices):
        RENT = 'rent', 'À louer'
        SALE = 'sale', 'À vendre'

    class Category(models.TextChoices):
        HOUSE = 'house', 'Maison'
        APARTMENT = 'apartment', 'Appartement'
        LAND = 'land', 'Terrain'
        OFFICE = 'office', 'Bureau'
        SHOP = 'shop', 'Magasin'

    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, related_name='listings')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='owned_listings')

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    category = models.CharField(max_length=20, choices=Category.choices)
    listing_type = models.CharField(max_length=10, choices=ListingType.choices)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=5, default="XOF")
    bedrooms = models.PositiveIntegerField(null=True, blank=True)
    bathrooms = models.PositiveIntegerField(null=True, blank=True)
    surface = models.PositiveIntegerField(null=True, blank=True, help_text="Surface en m²")
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.get_listing_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.agency.id}")
        super().save(*args, **kwargs)
        
    def can_view(self, user: User) -> bool:
        if not user.is_authenticated:
            return False
        if user.is_platform_admin():
            return True
        if user.is_agency_admin() and user.agency_id == self.agency_id:
            return True
        if user.is_agent() and self.owner_id == user.id:
            return True
        return False

    def can_edit(self, user: User) -> bool:
        # même logique que view pour l’édition
        return self.can_view(user)
    


class ListingPhoto(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField()
    is_cover = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Photo {self.id} de {self.listing.title}"