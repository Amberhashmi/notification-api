from django.urls import path
from .views import get_notifications, create_notification, mark_notification_as_read

urlpatterns = [
    path("notifications/", get_notifications),
    path("notifications/create/", create_notification),
    path("notifications/<int:id>/read/", mark_notification_as_read),
]