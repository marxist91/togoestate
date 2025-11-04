from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Notification


@login_required
def notification_list(request):
    """Display user's notifications"""
    notifications = Notification.objects.filter(user=request.user)

    # Filter by read status
    status_filter = request.GET.get('status')
    if status_filter == 'unread':
        notifications = notifications.filter(is_read=False)
    elif status_filter == 'read':
        notifications = notifications.filter(is_read=True)

    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        notifications = notifications.filter(
            Q(title__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'notifications': page_obj,
        'unread_count': Notification.get_unread_count(request.user),
        'status_filter': status_filter,
        'search_query': search_query,
    }

    return render(request, 'notifications/notification_list.html', context)


@login_required
@require_POST
def mark_as_read(request, notification_id):
    """Mark a specific notification as read"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.mark_as_read()

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Notification marquée comme lue.')
    return redirect('notifications:notification_list')


@login_required
@require_POST
def mark_all_as_read(request):
    """Mark all notifications as read for the current user"""
    count = Notification.mark_all_as_read(request.user)

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'count': count
        })

    messages.success(request, f'{count} notification(s) marquée(s) comme lue(s).')
    return redirect('notifications:notification_list')


@login_required
@require_POST
def delete_notification(request, notification_id):
    """Delete a specific notification"""
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        user=request.user
    )
    notification.delete()

    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        return JsonResponse({'success': True})

    messages.success(request, 'Notification supprimée.')
    return redirect('notifications:notification_list')


def notification_count(request):
    """API endpoint to get unread notification count"""
    if request.user.is_authenticated:
        count = Notification.get_unread_count(request.user)
    else:
        count = 0
    return JsonResponse({'count': count})


def notification_list_ajax(request):
    """API endpoint to get notifications list for AJAX"""
    if request.user.is_authenticated:
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:10]

        data = []
        for notification in notifications:
            data.append({
                'id': notification.id,
                'type': notification.notification_type,
                'title': notification.title,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at.strftime('%d/%m/%Y %H:%M'),
                'action_url': notification.action_url,
            })
    else:
        data = []

    return JsonResponse({'notifications': data})


# Utility functions for creating notifications
def create_appointment_notification(appointment, notification_type, recipient):
    """Create notification for appointment events"""
    from django.urls import reverse

    # Personnaliser les messages selon le rôle du destinataire
    if recipient.is_agency_admin():
        type_messages = {
            'appointment_request': {
                'title': 'Nouvelle demande de rendez-vous',
                'message': f'{appointment.customer.username} a demandé un rendez-vous avec {appointment.agent.username} pour "{appointment.listing.title}" le {appointment.scheduled_date.strftime("%d/%m/%Y à %H:%M")}.'
            },
            'appointment_confirmed': {
                'title': 'Rendez-vous confirmé',
                'message': f'Le rendez-vous de {appointment.customer.username} avec {appointment.agent.username} pour "{appointment.listing.title}" le {appointment.scheduled_date.strftime("%d/%m/%Y à %H:%M")} a été confirmé.'
            },
            'appointment_cancelled': {
                'title': 'Rendez-vous annulé',
                'message': f'Le rendez-vous de {appointment.customer.username} avec {appointment.agent.username} pour "{appointment.listing.title}" le {appointment.scheduled_date.strftime("%d/%m/%Y à %H:%M")} a été annulé.'
            },
            'appointment_completed': {
                'title': 'Rendez-vous terminé',
                'message': f'Le rendez-vous de {appointment.customer.username} avec {appointment.agent.username} pour "{appointment.listing.title}" est maintenant terminé.'
            }
        }
    else:
        type_messages = {
            'appointment_request': {
                'title': 'Nouvelle demande de rendez-vous',
                'message': f'{appointment.customer.username} a demandé un rendez-vous pour "{appointment.listing.title}" le {appointment.scheduled_date.strftime("%d/%m/%Y à %H:%M")}.'
            },
            'appointment_confirmed': {
                'title': 'Rendez-vous confirmé',
                'message': f'Votre rendez-vous pour "{appointment.listing.title}" le {appointment.scheduled_date.strftime("%d/%m/%Y à %H:%M")} a été confirmé.'
            },
            'appointment_cancelled': {
                'title': 'Rendez-vous annulé',
                'message': f'Votre rendez-vous pour "{appointment.listing.title}" le {appointment.scheduled_date.strftime("%d/%m/%Y à %H:%M")} a été annulé.'
            },
            'appointment_completed': {
                'title': 'Rendez-vous terminé',
                'message': f'Votre rendez-vous pour "{appointment.listing.title}" est maintenant terminé.'
            }
        }

    if notification_type in type_messages:
        data = type_messages[notification_type]
        action_url = reverse('appointment_detail', args=[appointment.id])

        Notification.create_notification(
            user=recipient,
            notification_type=notification_type,
            title=data['title'],
            message=data['message'],
            content_object=appointment,
            action_url=action_url
        )


def create_listing_notification(listing, notification_type, recipient):
    """Create notification for listing events"""
    from django.urls import reverse

    type_messages = {
        'listing_created': {
            'title': 'Nouvelle annonce créée',
            'message': f'Une nouvelle annonce "{listing.title}" a été créée par {listing.owner.username} dans l\'agence {listing.agency.name}.'
        },
        'listing_approved': {
            'title': 'Annonce approuvée',
            'message': f'Votre annonce "{listing.title}" a été approuvée et est maintenant visible sur la plateforme.'
        },
        'listing_rejected': {
            'title': 'Annonce rejetée',
            'message': f'Votre annonce "{listing.title}" a été rejetée. Veuillez vérifier les critères d\'approbation.'
        },
        'listing_featured': {
            'title': 'Annonce mise en avant',
            'message': f'Votre annonce "{listing.title}" a été mise en avant et bénéficie d\'une meilleure visibilité.'
        }
    }

    if notification_type in type_messages:
        data = type_messages[notification_type]
        action_url = reverse('listing_detail', args=[listing.slug])

        Notification.create_notification(
            user=recipient,
            notification_type=notification_type,
            title=data['title'],
            message=data['message'],
            content_object=listing,
            action_url=action_url
        )


def create_agency_notification(agency, notification_type, recipient):
    """Create notification for agency events"""
    from django.urls import reverse

    type_messages = {
        'agency_approved': {
            'title': 'Agence approuvée',
            'message': f'Votre agence "{agency.name}" a été approuvée et est maintenant active sur la plateforme.'
        },
        'agency_rejected': {
            'title': 'Agence rejetée',
            'message': f'Votre demande d\'agence "{agency.name}" a été rejetée. Veuillez contacter le support.'
        },
        'agent_joined': {
            'title': 'Nouvel agent',
            'message': f'Un nouvel agent a rejoint votre agence "{agency.name}".'
        }
    }

    if notification_type in type_messages:
        data = type_messages[notification_type]
        action_url = reverse('agency_detail', args=[agency.id]) if hasattr(agency, 'id') else None

        Notification.create_notification(
            user=recipient,
            notification_type=notification_type,
            title=data['title'],
            message=data['message'],
            content_object=agency,
            action_url=action_url
        )


def create_user_notification(user, notification_type, recipient):
    """Create notification for user-related events"""
    from django.urls import reverse

    type_messages = {
        'user_registered': {
            'title': 'Nouvel utilisateur inscrit',
            'message': f'Un nouvel utilisateur "{user.username}" s\'est inscrit sur la plateforme.'
        },
        'message_received': {
            'title': 'Message reçu',
            'message': f'Vous avez reçu un message de {user.username}.'
        }
    }

    if notification_type in type_messages:
        data = type_messages[notification_type]
        action_url = reverse('user_detail', args=[user.id]) if hasattr(user, 'id') else None

        Notification.create_notification(
            user=recipient,
            notification_type=notification_type,
            title=data['title'],
            message=data['message'],
            content_object=user,
            action_url=action_url
        )
