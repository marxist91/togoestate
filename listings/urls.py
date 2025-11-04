from django.urls import path

from . import views

urlpatterns = [
    path("", views.listing_list, name="listing_list"),              # /listings/
    path("region/<slug:region_slug>/", views.region_listings, name="region_listings"),  # /listings/region/<slug>/
    path("create/", views.listing_create, name="listing_create"),       # /listings/create/
    path("manage/", views.manage_listings, name="manage_listings"),     # /listings/manage/
    path("my-listings/", views.my_listings, name="my_listings"),         # /listings/my-listings/
    path("edit/<int:pk>/", views.listing_edit, name="listing_edit"),    # /listings/edit/12/
    path("delete/<int:pk>/", views.listing_delete, name="listing_delete"),  # /listings/delete/12/
    path("<slug:slug>/", views.listing_detail, name="listing_detail"),  # /listings/<slug>/
]
