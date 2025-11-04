from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from accounts.models import User


class Notification(models.Model):
    class NotificationType(models.TextChoices):
        # Appointment related
        APPOINTMENT_REQUEST = 'appointment_request', _('Demande de rendez-vous')
        APPOINTMENT_CONFIRMED = 'appointment_confirmed', _('Rendez-vous confirmé')
        APPOINTMENT_CANCELLED = 'appointment_cancelled', _('Rendez-vous annulé')
        APPOINTMENT_COMPLETED = 'appointment_completed', _('Rendez-vous terminé')

        # Listing related
        LISTING_APPROVED = 'listing_approved', _('Annonce approuvée')
        LISTING_REJECTED = 'listing_rejected', _('Annonce rejetée')
        LISTING_FEATURED = 'listing_featured', _('Annonce mise en avant')

        # Agency related
        AGENCY_APPROVED = 'agency_approved', _('Agence approuvée')
        AGENCY_REJECTED = 'agency_rejected', _('Agence rejetée')
        AGENT_JOINED = 'agent_joined', _('Agent rejoint l\'agence')

        # User related
        USER_REGISTERED = 'user_registered', _('Nouvel utilisateur inscrit')
        MESSAGE_RECEIVED = 'message_received', _('Message reçu')

        # System notifications
        SYSTEM_ALERT = 'system_alert', _('Alerte système')
        MAINTENANCE = 'maintenance', _('Maintenance programmée')

    # Recipient
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name=_('Utilisateur')
    )

    # Notification content
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        verbose_name=_('Type de notification')
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_('Titre')
    )

    message = models.TextField(
        verbose_name=_('Message')
    )

    # Related object (generic foreign key for flexibility)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='notifications'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Status
    is_read = models.BooleanField(
        default=False,
        verbose_name=_('Lu')
    )

    # URLs for actions
    action_url = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('URL d\'action')
    )

    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Créé le')
    )

    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Lu le')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Notification')
        verbose_name_plural = _('Notifications')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    def mark_as_read(self):
        """Mark notification as read"""
        from django.utils import timezone
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])

    @property
    def is_unread(self):
        return not self.is_read

    @classmethod
    def create_notification(cls, user, notification_type, title, message,
                          content_object=None, action_url=None):
        """Helper method to create notifications"""
        notification = cls(
            user=user,
            notification_type=notification_type,
            title=title,
            message=message,
            action_url=action_url
        )

        if content_object:
            notification.content_type = ContentType.objects.get_for_model(content_object)
            notification.object_id = content_object.pk

        notification.save()
        return notification

    @classmethod
    def get_unread_count(cls, user):
        """Get count of unread notifications for a user"""
        return cls.objects.filter(user=user, is_read=False).count()

    @classmethod
    def mark_all_as_read(cls, user):
        """Mark all notifications as read for a user"""
        from django.utils import timezone
        return cls.objects.filter(user=user, is_read=False).update(
            is_read=True,
            read_at=timezone.now()
        )
