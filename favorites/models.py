from django.db import models
from django.conf import settings
from listings.models import Listing


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    listing = models.ForeignKey(
        Listing,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'listing')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.listing.title}"
