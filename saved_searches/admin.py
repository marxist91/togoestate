from django.contrib import admin
from .models import SavedSearch, SearchHistory


@admin.register(SavedSearch)
class SavedSearchAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'query', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'name', 'query')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(SearchHistory)
class SearchHistoryAdmin(admin.ModelAdmin):
    list_display = ('user', 'query', 'results_count', 'searched_at')
    list_filter = ('searched_at',)
    search_fields = ('user__username', 'query')
    readonly_fields = ('searched_at',)
