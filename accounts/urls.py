from django.urls import path

from . import views
from .views import update_worker_status

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
    path(
        "worker/select-skills/",
        views.select_skills,
        name="worker-select-skills",
    ),
    path(
        "worker/status/",
        update_worker_status,
        name="worker-status",
    ),
    path(
        "worker/profile/",
        views.worker_profile,
        name="worker-profile",
    ),
    path("login/", views.user_login, name="user-login"),
    path("refresh/", views.user_refresh, name="user-refresh"),
    path("logout/", views.user_logout, name="user-logout"),
]
