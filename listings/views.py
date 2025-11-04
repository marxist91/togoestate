from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator

from .models import Listing
from agencies.models import City
from .query import listings_for_user
from core.permissions import require_role


@login_required
@require_role('agency_admin', 'agent')
def manage_listings(request):
    listings = listings_for_user(request.user)
    published_count = listings.filter(published=True).count()
    draft_count = listings.filter(published=False).count()
    return render(request, 'listings/manage_list.html', {
        'listings': listings,
        'published_count': published_count,
        'draft_count': draft_count,
    })


@login_required
@require_role('agency_admin', 'agent')
def listing_edit(request, pk):
    listing = get_object_or_404(Listing, pk=pk)
    if not listing.can_edit(request.user):
        messages.error(request, "Accès refusé.")
        return redirect('manage_listings')

    if request.method == 'POST':
        listing.title = request.POST.get('title', listing.title)
        # ... autres champs autorisés ...
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


@login_required
@require_role('agency_admin', 'agent')
def my_listings(request):
    listings = listings_for_user(request.user)
    published_count = listings.filter(published=True).count()
    draft_count = listings.filter(published=False).count()
    return render(request, 'listings/manage_list.html', {
        'listings': listings,
        'published_count': published_count,
        'draft_count': draft_count,
    })


@login_required
@require_role('agency_admin', 'agent')
def listing_create(request):
    from .forms import ListingForm
    from .models import ListingPhoto

    if request.method == 'POST':
        form = ListingForm(request.POST)
        if form.is_valid():
            listing = form.save(commit=False)
            listing.agency = request.user.agency
            listing.owner = request.user
            listing.save()

            # Gestion des photos uploadées
            photos = request.FILES.getlist('photos')
            for i, photo in enumerate(photos):
                ListingPhoto.objects.create(
                    listing=listing,
                    image=photo,
                    is_cover=(i == 0),  # Première photo comme couverture
                    order=i
                )

            messages.success(request, "Annonce créée avec succès.")
            return redirect('manage_listings')
    else:
        form = ListingForm()

    return render(request, 'listings/listing_form.html', {'form': form})


def listing_detail(request, slug):
    listing = get_object_or_404(Listing, slug=slug, published=True)

    # Préparer la photo de couverture et la galerie
    cover = listing.photos.filter(is_cover=True).first()
    if cover:
        gallery = listing.photos.exclude(pk=cover.pk).order_by("order")
    else:
        gallery = listing.photos.all().order_by("order")

    context = {
        "listing": listing,
        "cover": cover,
        "gallery": gallery,
    }
    return render(request, 'listings/listing_detail.html', context)


def listing_list(request):
    # Base queryset
    listings = Listing.objects.filter(published=True).select_related("city", "agency", "owner")

    # Filtres GET
    city_id = request.GET.get("city")
    category = request.GET.get("category")
    listing_type = request.GET.get("listing_type")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Filtres classiques
    if city_id:
        listings = listings.filter(city_id=city_id)
    if category:
        listings = listings.filter(category=category)  # si category est un CharField avec choices
    if listing_type:
        listings = listings.filter(listing_type=listing_type)
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(listings.order_by("-id"), 12)  # 12 annonces par page
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Préparer la photo de couverture pour chaque annonce
    for l in page_obj:
        l.cover = l.photos.filter(is_cover=True).first()

    # Régions (affichage)
    regions = [
        {"name": "Maritime", "slug": "maritime"},
        {"name": "Plateaux", "slug": "plateaux"},
        {"name": "Centrale", "slug": "centrale"},
        {"name": "Kara", "slug": "kara"},
        {"name": "Savanes", "slug": "savanes"},
    ]

    # Annonces en vedette (si champ featured)
    featured = Listing.objects.filter(published=True, featured=True).select_related("city")[:6]
    for f in featured:
        f.cover = f.photos.filter(is_cover=True).first()

    # Données pour les <select>
    cities = City.objects.all().order_by("name")
    categories = [(choice[0], choice[1]) for choice in Listing.Category.choices]
    types = [(choice[0], choice[1]) for choice in Listing.ListingType.choices]

    context = {
        "page_obj": page_obj,
        "cities": cities,
        "categories": categories,
        "types": types,
        "regions": regions,
        "featured": featured,
        "stats": {
            "total": Listing.objects.filter(published=True).count(),
        },
        "filters": {
            "city": city_id or "",
            "category": category or "",
            "listing_type": listing_type or "",
            "min_price": min_price or "",
            "max_price": max_price or "",
        }
    }
    return render(request, "listings/listing_list.html", context)


def region_listings(request, region_slug):
    from agencies.models import Region

    # Récupérer la région par slug
    try:
        region = Region.objects.get(slug=region_slug)
    except Region.DoesNotExist:
        from django.http import Http404
        raise Http404("Région non trouvée")

    # Filtrer les annonces par région
    listings = Listing.objects.filter(
        published=True,
        city__district__region=region
    ).select_related("city", "agency", "owner")

    # Filtres GET supplémentaires (optionnels)
    city_id = request.GET.get("city")
    category = request.GET.get("category")
    listing_type = request.GET.get("listing_type")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    # Appliquer les filtres supplémentaires
    if city_id:
        listings = listings.filter(city_id=city_id)
    if category:
        listings = listings.filter(category=category)
    if listing_type:
        listings = listings.filter(listing_type=listing_type)
    if min_price:
        listings = listings.filter(price__gte=min_price)
    if max_price:
        listings = listings.filter(price__lte=max_price)

    # Pagination
    paginator = Paginator(listings.order_by("-id"), 12)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Préparer la photo de couverture pour chaque annonce
    for l in page_obj:
        l.cover = l.photos.filter(is_cover=True).first()

    # Villes de cette région pour les filtres
    cities = City.objects.all().order_by("name")
    categories = [(choice[0], choice[1]) for choice in Listing.Category.choices]
    types = [(choice[0], choice[1]) for choice in Listing.ListingType.choices]

    context = {
        "region": region,
        "page_obj": page_obj,
        "cities": cities,
        "categories": categories,
        "types": types,
        "stats": {
            "total": listings.count(),
        },
        "filters": {
            "city": city_id or "",
            "category": category or "",
            "listing_type": listing_type or "",
            "min_price": min_price or "",
            "max_price": max_price or "",
        }
    }
    return render(request, "listings/region_listings.html", context)
