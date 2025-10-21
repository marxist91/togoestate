# listings/query.py
from .models import Listing
def listings_for_user(user):
   
    qs = Listing.objects.all()
    if user.is_platform_admin():
        return qs
    if user.is_agency_admin():
        return qs.filter(agency=user.agency)
    if user.is_agent():
        return qs.filter(owner=user)
    return Listing.objects.none()