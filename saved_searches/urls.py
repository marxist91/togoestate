from django.urls import path
from . import views

app_name = 'saved_searches'

urlpatterns = [
    path('save/', views.save_search, name='save_search'),
    path('list/', views.saved_searches_list, name='saved_searches_list'),
    path('delete/<int:search_id>/', views.delete_saved_search, name='delete_saved_search'),
    path('history/', views.search_history, name='search_history'),
    path('record/', views.record_search, name='record_search'),
]
