import pytest
from django.urls import reverse, NoReverseMatch

@pytest.mark.parametrize("route,args", [
    ("cockpit_admin:accounts_user_changelist", []),
    ("cockpit_admin:accounts_user_add", []),
    ("cockpit_admin:accounts_user_change", [1]),
    ("cockpit_admin:agencies_agency_changelist", []),
    ("cockpit_admin:listings_listing_changelist", []),
])
def test_admin_routes_exist(route, args):
    try:
        url = reverse(route, args=args)
        assert url.startswith("/cockpit/")
    except NoReverseMatch:
        pytest.fail(f"Route {route} introuvable")