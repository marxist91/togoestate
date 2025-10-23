from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"

    def __str__(self):
        return self.name


class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name="districts")
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Quartier"
        verbose_name_plural = "Quartiers"
        unique_together = ("city", "name")

    def __str__(self):
        return f"{self.name} ({self.city.name})"