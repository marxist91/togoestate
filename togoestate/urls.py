"""
URL configuration for togoestate project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from . import views

# ⚠️ Import de ton AuditAdminSite centralisé
from core.admin_site import admin_site

urlpatterns = [
    # 👉 expose ton cockpit admin sous /cockpit/
    path("cockpit/", admin_site.urls),

    # 👉 si tu veux garder l’admin Django classique
    path("admin/", admin.site.urls),

    # autres routes
    path("listings/", include("listings.urls")),
    path("api/", include("listings.urls_api")),
    path("accounts/", include("accounts.urls")),
    path("saved_searches/", include("saved_searches.urls")),
    path("favorites/", include("favorites.urls")),
    path("notifications/", include("notifications.urls")),
    path("", views.home, name="home"),
    path("about/", views.about, name="about"),
    path("contact/", views.contact, name="contact"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)