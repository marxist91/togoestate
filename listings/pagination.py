from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from rest_framework.response import Response

class MixedPagination(PageNumberPagination, LimitOffsetPagination):
    """
    Pagination mixte : accepte soit ?page=2&page_size=10
    soit ?limit=10&offset=20
    """
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100

    def paginate_queryset(self, queryset, request, view=None):
        # Si "limit" ou "offset" sont présents → LimitOffsetPagination
        if "limit" in request.query_params or "offset" in request.query_params:
            return LimitOffsetPagination.paginate_queryset(self, queryset, request, view)
        # Sinon → PageNumberPagination
        return PageNumberPagination.paginate_queryset(self, queryset, request, view)

    def get_paginated_response(self, data):
        if hasattr(self, "limit") and self.limit is not None:
            # Mode limit/offset
            return LimitOffsetPagination.get_paginated_response(self, data)
        # Mode page/page_size
        return PageNumberPagination.get_paginated_response(self, data)