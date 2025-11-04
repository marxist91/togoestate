import pytest
from rest_framework.test import APIClient

from listings.models import Listing, City
from django.contrib.auth import get_user_model
User = get_user_model()

@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def city(db):
    return City.objects.create(name="Lomé")


@pytest.fixture
def agency_admin(db):
    user = User.objects.create_user(username="admin", password="pass")
    user.roles = ["agency_admin"]  # ⚠️ adapte selon ton système de rôles
    user.save()
    return user


@pytest.fixture
def agent(db):
    user = User.objects.create_user(username="agent", password="pass")
    user.roles = ["agent"]
    user.save()
    return user


@pytest.fixture
def normal_user(db):
    return User.objects.create_user(username="normal", password="pass")


@pytest.fixture
def listing(db, city, agency_admin):
    return Listing.objects.create(
        title="Maison test",
        slug="maison-test",
        price=100000,
        currency="XOF",
        city=city,
        category="Maison",
        listing_type="Vente",
        surface=120,
        bedrooms=3,
        bathrooms=2,
        address="Rue 123",
        owner=agency_admin,
        published=True,
    )


# --- TESTS ---

def test_get_listings(api_client, listing):
    response = api_client.get("/listings/api/listings/")
    assert response.status_code == 200
    assert response.data["count"] >= 1
    assert response.data["results"][0]["title"] == "Maison test"


def test_get_listing_detail(api_client, listing):
    response = api_client.get(f"/listings/api/listings/{listing.slug}/")
    assert response.status_code == 200
    assert response.data["slug"] == "maison-test"


def test_post_listing_requires_auth(api_client, city):
    data = {
        "title": "Nouvelle maison",
        "slug": "nouvelle-maison",
        "price": 200000,
        "currency": "XOF",
        "city": city.id,
        "category": "Maison",
        "listing_type": "Vente",
        "surface": 150,
        "bedrooms": 4,
        "bathrooms": 3,
        "address": "Rue 456",
        "description": "Superbe maison",
        "published": True,
    }
    response = api_client.post("/listings/api/listings/", data)
    assert response.status_code == 403  # interdit sans rôle


def test_post_listing_as_agent(api_client, agent, city):
    api_client.force_authenticate(user=agent)
    data = {
        "title": "Maison agent",
        "slug": "maison-agent",
        "price": 300000,
        "currency": "XOF",
        "city": city.id,
        "category": "Maison",
        "listing_type": "Vente",
        "surface": 180,
        "bedrooms": 4,
        "bathrooms": 2,
        "address": "Rue 789",
        "description": "Maison créée par agent",
        "published": True,
    }
    response = api_client.post("/listings/api/listings/", data)
    assert response.status_code == 201
    assert response.data["title"] == "Maison agent"


def test_put_listing_as_admin(api_client, agency_admin, listing):
    api_client.force_authenticate(user=agency_admin)
    url = f"/listings/api/listings/{listing.slug}/"
    response = api_client.put(url, {
        "title": "Maison modifiée",
        "slug": "maison-test",
        "price": 150000,
        "currency": "XOF",
        "city": listing.city.id,
        "category": "Maison",
        "listing_type": "Vente",
        "surface": 130,
        "bedrooms": 3,
        "bathrooms": 2,
        "address": "Rue 123",
        "description": "Modifiée",
        "published": True,
    })
    assert response.status_code == 200
    assert response.data["title"] == "Maison modifiée"


def test_delete_listing_as_normal_user(api_client, normal_user, listing):
    api_client.force_authenticate(user=normal_user)
    url = f"/listings/api/listings/{listing.slug}/"
    response = api_client.delete(url)
    assert response.status_code == 403  # interdit


def test_delete_listing_as_agent(api_client, agent, listing):
    api_client.force_authenticate(user=agent)
    url = f"/listings/api/listings/{listing.slug}/"
    response = api_client.delete(url)
    assert response.status_code in (204, 403)  # 204 si agent autorisé, 403 sinon