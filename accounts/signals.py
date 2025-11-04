from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import User, Appointment
from listings.models import Listing

@receiver(post_save, sender=User)
def set_role_for_superuser(sender, instance, created, **kwargs):
    """
    Si un superuser est créé, on force son rôle à admin_platform.
    """
    if created and instance.is_superuser:
        if instance.role != User.Roles.ADMIN_PLATFORM:
            instance.role = User.Roles.ADMIN_PLATFORM
            instance.save()


@receiver(post_save, sender=User)
def notify_agency_admin_on_agent_join(sender, instance, created, **kwargs):
    """
    Notifier l'admin de l'agence lorsqu'un nouvel agent rejoint l'agence
    """
    from notifications.views import create_agency_notification

    if created and instance.is_agent() and instance.agency:
        # Trouver l'admin de l'agence
        agency_admin = User.objects.filter(
            agency=instance.agency,
            role=User.Roles.AGENCY_ADMIN
        ).first()

        if agency_admin:
            create_agency_notification(
                agency=instance.agency,
                notification_type='agent_joined',
                recipient=agency_admin
            )


@receiver(post_save, sender=Appointment)
def create_appointment_notifications(sender, instance, created, **kwargs):
    """
    Créer des notifications lors de la création ou modification d'un rendez-vous
    """
    from notifications.views import create_appointment_notification

    # Trouver l'admin de l'agence de l'agent
    agency_admin = None
    if instance.agent.agency:
        agency_admin = User.objects.filter(
            agency=instance.agent.agency,
            role=User.Roles.AGENCY_ADMIN
        ).first()

    if created:
        # Notification pour l'agent (demande de rendez-vous)
        create_appointment_notification(
            appointment=instance,
            notification_type='appointment_request',
            recipient=instance.agent
        )

        # Notification pour l'admin de l'agence
        if agency_admin:
            create_appointment_notification(
                appointment=instance,
                notification_type='appointment_request',
                recipient=agency_admin
            )
    else:
        # Vérifier si le statut a changé
        if instance.status == 'confirmed':
            # Notification pour le client (rendez-vous confirmé)
            create_appointment_notification(
                appointment=instance,
                notification_type='appointment_confirmed',
                recipient=instance.customer
            )

            # Notification pour l'admin de l'agence
            if agency_admin:
                create_appointment_notification(
                    appointment=instance,
                    notification_type='appointment_confirmed',
                    recipient=agency_admin
                )
        elif instance.status == 'cancelled':
            # Notification pour le client (rendez-vous annulé)
            create_appointment_notification(
                appointment=instance,
                notification_type='appointment_cancelled',
                recipient=instance.customer
            )

            # Notification pour l'admin de l'agence
            if agency_admin:
                create_appointment_notification(
                    appointment=instance,
                    notification_type='appointment_cancelled',
                    recipient=agency_admin
                )
        elif instance.status == 'completed':
            # Notification pour le client (rendez-vous terminé)
            create_appointment_notification(
                appointment=instance,
                notification_type='appointment_completed',
                recipient=instance.customer
            )

            # Notification pour l'admin de l'agence
            if agency_admin:
                create_appointment_notification(
                    appointment=instance,
                    notification_type='appointment_completed',
                    recipient=agency_admin
                )


@receiver(post_save, sender=Listing)
def create_listing_notifications(sender, instance, created, **kwargs):
    """
    Créer des notifications lors de la création d'une annonce
    """
    from notifications.views import create_listing_notification

    if created:
        # Notification pour l'admin de l'agence
        agency_admin = User.objects.filter(
            agency=instance.agency,
            role=User.Roles.AGENCY_ADMIN
        ).first()
        if agency_admin:
            create_listing_notification(
                listing=instance,
                notification_type='listing_created',
                recipient=agency_admin
            )

        # Notification pour l'admin plateforme
        platform_admins = User.objects.filter(role=User.Roles.ADMIN_PLATFORM)
        for admin in platform_admins:
            create_listing_notification(
                listing=instance,
                notification_type='listing_created',
                recipient=admin
            )
