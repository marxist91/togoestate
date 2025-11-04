from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    # Main notification views
    path('', views.notification_list, name='notification_list'),

    # AJAX endpoints
    path('api/count/', views.notification_count, name='notification_count'),
    path('api/list/', views.notification_list_ajax, name='notification_list_ajax'),

    # Actions
    path('<int:notification_id>/read/', views.mark_as_read, name='mark_as_read'),
    path('mark-all-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
]
