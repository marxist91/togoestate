# core/permissions.py
from django.core.exceptions import PermissionDenied

def require_role(*roles):
    def wrapper(view_func):
        def _wrapped(request, *args, **kwargs):
            user = request.user
            if not user.is_authenticated:
                raise PermissionDenied
            if user.is_platform_admin():
                return view_func(request, *args, **kwargs)
            if 'agency_admin' in roles and user.is_agency_admin():
                return view_func(request, *args, **kwargs)
            if 'agent' in roles and user.is_agent():
                return view_func(request, *args, **kwargs)
            raise PermissionDenied
        return _wrapped
    return wrapper