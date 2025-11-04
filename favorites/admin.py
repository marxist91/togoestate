from django.contrib import admin
from .models import Favorite


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'listing', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'listing__title')
    readonly_fields = ('created_at',)
