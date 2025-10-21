# listings/api_views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from .models import Listing
from .query import listings_for_user
from core.drf_permissions import ListingAccessPermission

class ListingSerializer(ModelSerializer):
    class Meta:
        model = Listing
        fields = '__all__'
        read_only_fields = ('agency', 'owner')

class ListingViewSet(ModelViewSet):
    serializer_class = ListingSerializer
    permission_classes = [ListingAccessPermission]

    def get_queryset(self):
        return listings_for_user(self.request.user)

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(agency=user.agency, owner=user)