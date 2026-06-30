from django.urls import path

from . import views

urlpatterns = [
    path(
        "customer/signup/",
        views.customer_signup,
        name="customer-signup",
    ),
    path(
        "worker/signup/",
        views.worker_signup,
        name="worker-signup",
    ),
    path(
        "customer/login",
        views.customer_login,
        name="customer-login"
    ),
    path(
        "customer/refresh",
        views.customer_refresh,
        name="customer-refresh"
    )
    path(
        "customer/logout",
        views.customer_logout,
        name="customer-logout"
    )
]
