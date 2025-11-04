from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny
from django_filters.rest_framework import DjangoFilterBackend

from .models import Listing
from .serializers import (
    ListingReadSerializer,
    ListingWriteSerializer,
    ListingSerializer,  # alias = ListingReadSerializer
)
from .permissions import IsAgencyStaff
from .filters import ListingFilter


class ListingViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """
    API CRUD pour les annonces :
    - GET list/detail : public (annonces publiées uniquement)
    - POST/PUT/PATCH/DELETE : réservés aux rôles agency_admin / agent
    """

    queryset = Listing.objects.select_related("city", "agency", "owner")
    filter_backends = [DjangoFilterBackend]
    filterset_class = ListingFilter
    lookup_field = "slug"  # permet d'utiliser /api/listings/<slug>/

    def get_permissions(self):
        if self.request.method in ("GET",):
            return [AllowAny()]
        return [IsAgencyStaff()]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.request.method in ("GET",):
            return qs.filter(published=True)
        return qs

    def get_serializer_class(self):
        """
        - Lecture (GET) : ListingReadSerializer (alias ListingSerializer)
        - Écriture (POST/PUT/PATCH) : ListingWriteSerializer
        """
        if self.request.method in ("POST", "PUT", "PATCH"):
            return ListingWriteSerializer
        return ListingReadSerializer  # ou ListingSerializer (alias)

    def perform_create(self, serializer):
        # Associer automatiquement l’utilisateur comme owner
        serializer.save(owner=self.request.user)

    def perform_update(self, serializer):
        instance = self.get_object()
        if hasattr(instance, "can_edit") and not instance.can_edit(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Accès refusé.")
        serializer.save()

    def perform_destroy(self, instance):
        if hasattr(instance, "can_edit") and not instance.can_edit(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Accès refusé.")
        instance.delete()