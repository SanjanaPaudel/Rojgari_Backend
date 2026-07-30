from django.urls import path

from . import views

urlpatterns = [
    path(
        "device-token/",
        views.register_device_token,
        name="device-token",
    ),

    path(
        "",
        views.notification_list,
        name="notification-list",
    ),
]

