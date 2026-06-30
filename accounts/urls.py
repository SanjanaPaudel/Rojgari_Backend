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
    path("login/", views.user_login, name="user-login"),
    path("refresh/", views.user_refresh, name="user-refresh"),
    path("logout/", views.user_logout, name="user-logout"),
]
