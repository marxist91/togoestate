from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from agencies.models import Agency


class User(AbstractUser):
    class Roles(models.TextChoices):
        ADMIN_PLATFORM = 'admin_platform', _('Admin plateforme')
        AGENCY_ADMIN = 'agency_admin', _('Admin agence')
        AGENT = 'agent', _('Agent')
        CUSTOMER = 'customer', _('Client')

    role = models.CharField(
        max_length=20,
        choices=Roles.choices,
        default=Roles.CUSTOMER,
    )
    roles = models.JSONField(default=list, null=True, blank=True)

    agency = models.ForeignKey(
       "agencies.Agency",
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='users'
    )

    def is_platform_admin(self):
        return self.role == self.Roles.ADMIN_PLATFORM

    def is_agency_admin(self):
        return self.role == self.Roles.AGENCY_ADMIN

    def is_agent(self):
        return self.role == self.Roles.AGENT

    def is_customer(self):
        return self.role == self.Roles.CUSTOMER

    def __str__(self):
        return f"{self.username} ({self.role})"


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', _('En attente')
        CONFIRMED = 'confirmed', _('Confirmé')
        CANCELLED = 'cancelled', _('Annulé')
        COMPLETED = 'completed', _('Terminé')

    # Relations
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name='appointments'
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='agent_appointments',
        limit_choices_to={'role': 'agent'}
    )
    customer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='customer_appointments',
        limit_choices_to={'role': 'customer'}
    )

    # Détails du rendez-vous
    scheduled_date = models.DateTimeField()
    duration_minutes = models.PositiveIntegerField(default=60)
    notes = models.TextField(blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )

    # Métadonnées
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-scheduled_date']
        unique_together = ['listing', 'scheduled_date', 'agent']

    def __str__(self):
        return f"Rendez-vous {self.listing.title} - {self.scheduled_date.strftime('%d/%m/%Y %H:%M')}"

    @property
    def is_past(self):
        from django.utils import timezone
        return self.scheduled_date < timezone.now()

    @property
    def can_be_modified(self):
        """Un rendez-vous peut être modifié s'il n'est pas passé et pas annulé"""
        return not self.is_past and self.status != self.Status.CANCELLED


class UserActivity(models.Model):
    class ActivityType(models.TextChoices):
        # Authentication
        LOGIN = 'login', _('Connexion')
        LOGOUT = 'logout', _('Déconnexion')

        # Profile
        PROFILE_UPDATE = 'profile_update', _('Mise à jour du profil')
        PASSWORD_CHANGE = 'password_change', _('Changement de mot de passe')

        # Listings
        LISTING_VIEW = 'listing_view', _('Consultation d\'annonce')
        LISTING_CREATE = 'listing_create', _('Création d\'annonce')
        LISTING_UPDATE = 'listing_update', _('Modification d\'annonce')
        LISTING_DELETE = 'listing_delete', _('Suppression d\'annonce')
        LISTING_PUBLISH = 'listing_publish', _('Publication d\'annonce')

        # Favorites
        FAVORITE_ADD = 'favorite_add', _('Ajout aux favoris')
        FAVORITE_REMOVE = 'favorite_remove', _('Retrait des favoris')

        # Saved Searches
        SEARCH_SAVE = 'search_save', _('Sauvegarde de recherche')
        SEARCH_UPDATE = 'search_update', _('Modification de recherche')
        SEARCH_DELETE = 'search_delete', _('Suppression de recherche')

        # Appointments
        APPOINTMENT_REQUEST = 'appointment_request', _('Demande de rendez-vous')
        APPOINTMENT_CONFIRM = 'appointment_confirm', _('Confirmation de rendez-vous')
        APPOINTMENT_CANCEL = 'appointment_cancel', _('Annulation de rendez-vous')
        APPOINTMENT_COMPLETE = 'appointment_complete', _('Rendez-vous terminé')

        # User Management (Agency Admin)
        AGENT_ADD = 'agent_add', _('Ajout d\'agent')
        AGENT_UPDATE = 'agent_update', _('Modification d\'agent')
        AGENT_REMOVE = 'agent_remove', _('Suppression d\'agent')

        # Agency Management (Platform Admin)
        AGENCY_APPROVE = 'agency_approve', _('Approbation d\'agence')
        AGENCY_REJECT = 'agency_reject', _('Rejet d\'agence')
        AGENCY_UPDATE = 'agency_update', _('Modification d\'agence')

        # System (Platform Admin)
        USER_CREATE = 'user_create', _('Création d\'utilisateur')
        USER_UPDATE = 'user_update', _('Modification d\'utilisateur')
        USER_DELETE = 'user_delete', _('Suppression d\'utilisateur')

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('Utilisateur')
    )

    activity_type = models.CharField(
        max_length=50,
        choices=ActivityType.choices,
        verbose_name=_('Type d\'activité')
    )

    title = models.CharField(
        max_length=200,
        verbose_name=_('Titre')
    )

    description = models.TextField(
        blank=True,
        verbose_name=_('Description')
    )

    # Related object (generic foreign key for flexibility)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_activities'
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional data (JSON for extensibility)
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_('Métadonnées')
    )

    # IP address and user agent for security tracking
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Adresse IP')
    )

    user_agent = models.TextField(
        blank=True,
        verbose_name=_('User Agent')
    )

    # Timestamp
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Créé le')
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Activité utilisateur')
        verbose_name_plural = _('Activités utilisateurs')
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.user.username}: {self.title}"

    @classmethod
    def log_activity(cls, user, activity_type, title, description='',
                    content_object=None, metadata=None, request=None):
        """Helper method to log user activities"""
        activity = cls(
            user=user,
            activity_type=activity_type,
            title=title,
            description=description,
            metadata=metadata or {}
        )

        if content_object:
            activity.content_type = ContentType.objects.get_for_model(content_object)
            activity.object_id = content_object.pk

        if request:
            activity.ip_address = cls.get_client_ip(request)
            activity.user_agent = request.META.get('HTTP_USER_AGENT', '')

        activity.save()
        return activity

    @staticmethod
    def get_client_ip(request):
        """Get the client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
