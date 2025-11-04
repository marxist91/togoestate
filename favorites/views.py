from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from listings.models import Listing
from .models import Favorite


@login_required
@require_POST
def toggle_favorite(request, listing_id):
    listing = get_object_or_404(Listing, id=listing_id)
    favorite, created = Favorite.objects.get_or_create(
        user=request.user,
        listing=listing
    )

    if not created:
        favorite.delete()
        return JsonResponse({'success': True, 'is_favorite': False})

    return JsonResponse({'success': True, 'is_favorite': True})


@login_required
def favorites_list(request):
    favorites = Favorite.objects.filter(user=request.user).select_related('listing')
    return JsonResponse({
        'favorites': [
            {
                'id': fav.id,
                'listing': {
                    'id': fav.listing.id,
                    'title': fav.listing.title,
                    'price': str(fav.listing.price),
                    'city': fav.listing.city.name if fav.listing.city else '',
                    'slug': fav.listing.slug,
                },
                'created_at': fav.created_at.isoformat()
            }
            for fav in favorites
        ]
    })
