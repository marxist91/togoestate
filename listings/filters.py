import django_filters
from .models import Listing

class ListingFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    city = django_filters.CharFilter(field_name="city__id", lookup_expr="exact")
    category = django_filters.CharFilter(field_name="category", lookup_expr="iexact")

    class Meta:
        model = Listing
        fields = ["city", "category", "min_price", "max_price"]