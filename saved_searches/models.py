from django.db import models
from django.conf import settings


class SavedSearch(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_searches'
    )
    name = models.CharField(max_length=100, blank=True)
    query = models.TextField()  # JSON string containing search parameters
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.name or self.query[:50]}"


class SearchHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='search_history'
    )
    query = models.TextField()
    results_count = models.PositiveIntegerField(default=0)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.user.username} - {self.query[:50]}"
