from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'notification_type',
        'title',
        'is_read',
        'created_at',
        'read_at'
    ]

    list_filter = [
        'notification_type',
        'is_read',
        'created_at',
        'read_at'
    ]

    search_fields = [
        'user__username',
        'user__email',
        'title',
        'message'
    ]

    readonly_fields = [
        'created_at',
        'read_at'
    ]

    ordering = ['-created_at']

    fieldsets = (
        (_('Informations générales'), {
            'fields': ('user', 'notification_type', 'title', 'message')
        }),
        (_('Objet lié'), {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        (_('Statut'), {
            'fields': ('is_read', 'read_at')
        }),
        (_('Actions'), {
            'fields': ('action_url',),
            'classes': ('collapse',)
        }),
        (_('Métadonnées'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(
            request,
            ngettext(
                '%d notification marquée comme lue.',
                '%d notifications marquées comme lues.',
                updated,
            ) % updated,
        )
    mark_as_read.short_description = _("Marquer comme lue(s)")

    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(
            request,
            ngettext(
                '%d notification marquée comme non lue.',
                '%d notifications marquées comme non lues.',
                updated,
            ) % updated,
        )
    mark_as_unread.short_description = _("Marquer comme non lue(s)")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'content_type')
