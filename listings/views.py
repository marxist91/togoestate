from django.shortcuts import render, get_object_or_404,redirect

from .models import Listing
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .query import listings_for_user
from core.permissions import require_role

@login_required
@require_role('agency_admin', 'agent')
def manage_listings(request):
    listings = listings_for_user(request.user)
    return render(request, 'listings/manage_list.html', {'listings':listings})


@login_required
@require_role('agency_admin', 'agent')
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    # contrôle fin d’édition
    if not listing.can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('manage_listings')

    if request.method == 'POST':
        # mettre à jour les champs autorisés
        listing.title = request.POST.get('title', listing.title)
        # ... autres champs ...
        listing.save()
        messages.success(request, "Annonce mise à jour.")
        return redirect('manage_listings')

    return render(request, 'listings/listing_form.html', {'listing': listing})

@login_required
@require_role('agency_admin', 'agent')
def listing_delete(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if not listing.can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('manage_listings')
    listing.delete()
    messages.success(request, "Annonce supprimée.")
    return redirect('manage_listings')


def listing_list(request):
    listings = Listing.objects.filter(published=True)
    return render(request, 'listings/listing_list.html', {'listings': listings})

def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug, published=True)
    return render(request, 'listings/listing_detail.html', {'listing': listing})