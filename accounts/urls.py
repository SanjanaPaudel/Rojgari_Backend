from django.urls import path

from . import views

urlpatterns = [
    path(
        "signup/",
        views.signup,
        name="signup",
    ),
    path(
        "verify-otp/",
        views.verify_otp,
        name="verify-otp",
    ),
    path(
        "resend-otp/",
        views.resend_otp,
        name="resend-otp",
    ),
    path(
        "worker/skills/",
        views.get_skills,
        name="worker-skills",
    ),
    path(
        "worker/dashboard/",
        views.worker_dashboard,
        name="worker-dashboard",
    ),
    path("login/", views.user_login, name="user-login"),
    path("refresh/", views.user_refresh, name="user-refresh"),
    path("logout/", views.user_logout, name="user-logout"),
]
