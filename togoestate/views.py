# togoestate/views.py
from django.shortcuts import render
from accounts.models import Agency, User
from listings.models import Listing
from django.db.models import Count
from django.db import models
from django.utils.timezone import now
from datetime import timedelta

from django.db.models.functions import TruncMonth
from django.db.models import Count
from itertools import chain

def home(request):
    stats = {
        "agencies_count": Agency.objects.count(),
        "listings_count": Listing.objects.filter(published=True).count(),
        "users_count": User.objects.count(),
    }

    recent_listings = Listing.objects.filter(published=True).order_by('-created_at')[:3]
    recent_agencies = Agency.objects.order_by('-created_at')[:3]
    
   # Construire une timeline normalisée
    events = []

    for l in Listing.objects.filter(published=True).order_by('-created_at')[:5]:
        events.append({
            "type": "Annonce",
            "title": l.title,
            "city": l.city,
            "timestamp": l.created_at,
            "icon": "🏠",
        })

    for a in Agency.objects.order_by('-created_at')[:5]:
        events.append({
            "type": "Agence",
            "title": a.name,
            "city": a.city,
            "timestamp": a.created_at,
            "icon": "🏢",

        })

    for u in User.objects.order_by('-date_joined')[:5]:
        events.append({
            "type": "Utilisateur",
            "title": u.username,
            "city": getattr(u.agency, "city", "-") if hasattr(u, "agency") and u.agency else "-",
            "timestamp": u.date_joined,
            "icon": "👤",
        })

    # Trier tous les événements par date
    events = sorted(events, key=lambda x: x["timestamp"], reverse=True)[:10]




    # Agrégation par mois (6 derniers mois)
    six_months_ago = now() - timedelta(days=180)
    listings_by_month = (
        Listing.objects.filter(created_at__gte=six_months_ago, published=True)
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Count('id'))
        .order_by('month')
    )

    return render(request, "home.html", {
        "stats": stats,
        "recent_listings": recent_listings,
        "recent_agencies": recent_agencies,
        "listings_by_month": list(listings_by_month),
        "recent_events": events,

    })