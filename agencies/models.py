from django.db import models
from django.utils.text import slugify


class Region(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    class Meta:
        verbose_name = "Région"
        verbose_name_plural = "Régions"
        ordering = ["name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class District(models.Model):
    name = models.CharField(max_length=100)
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name="districts")

    class Meta:
        verbose_name = "District"
        verbose_name_plural = "Districts"
        unique_together = ("name", "region")
        ordering = ["region__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.region.name})"


class City(models.Model):
    name = models.CharField(max_length=100)
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name="cities")

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"
        unique_together = ("name", "district")
        ordering = ["district__region__name", "district__name", "name"]

    def __str__(self):
        return f"{self.name} ({self.district.name}, {self.district.region.name})"


class Agency(models.Model):
    name = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True)

    # 🔑 FK vers City
    city = models.ForeignKey(
        "agencies.City",
        on_delete=models.PROTECT,
        related_name="agencies",
        null=True,
        blank=True
    )

    address = models.CharField(max_length=255, blank=True)
    description = models.TextField(blank=True)
    logo_url = models.URLField(blank=True)
    verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Agence"
        verbose_name_plural = "Agences"
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or f"agency-{self.pk or ''}"
            slug = base_slug
            i = 1
            while Agency.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{i}"
                i += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    # Helpers cockpit-ready
    @property
    def district(self):
        return self.city.district if self.city else None

    @property
    def region(self):
        return self.city.district.region if self.city else None