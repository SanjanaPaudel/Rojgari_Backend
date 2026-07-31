from django.urls import path

from . import views

urlpatterns = [
    path("device-token/", views.register_device_token, name="device-token"),
    path("", views.notification_list, name="notification-list"),
    path(
        "<int:notification_id>/read/",
        views.mark_notification_read,
        name="mark-notification-read",
    ),
    path(
        "unread-count/",
        views.unread_notification_count,
        name="unread-notification-count",
    ),
]
