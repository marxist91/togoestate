# listings/urls_api.py
from rest_framework.routers import DefaultRouter
from .api_views import ListingViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
urlpatterns = router.urls