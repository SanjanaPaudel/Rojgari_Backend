from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.admin_login),
    path("create/", views.create_admin),
    path("verify-otp/", views.verify_admin_otp),
    path("dashboard/", views.dashboard),
    # Worker management
    path("workers/", views.all_workers),
    path("workers/statistics/", views.worker_statistics),
    path("workers/pending/", views.pending_workers),
    path("workers/verified/", views.verified_workers),
    path(
        "workers/<int:worker_id>/",
        views.worker_details,
    ),
    path(
        "workers/<int:worker_id>/approve/",
        views.approve_worker,
    ),
    path(
        "workers/<int:worker_id>/reject/",
        views.reject_worker,
    ),
    path(
        "workers/<int:worker_id>/request-resubmission/",
        views.request_resubmission,
    ),
    # Category management
    path(
        "categories/",
        views.categories,
    ),
    path(
        "categories/<int:category_id>/",
        views.category_detail,
    ),
    path(
        "bookings/",
        views.admin_bookings_list,
        name="admin-bookings-list",
    ),
    path(
        "bookings/<int:booking_id>/",
        views.admin_booking_detail,
        name="admin-booking-detail",
    ),
    path(
        "profile/",
        views.admin_profile,
        name="admin-profile",
    ),
    path(
        "profile/photo/",
        views.admin_profile_photo,
        name="admin-profile-photo",
    ),
    path(
        "change-password/",
        views.change_admin_password,
        name="change-admin-password",
    ),
    path(
        "reports/bookings-trend/",
        views.admin_bookings_trend,
        name="admin-reports-bookings-trend",
    ),
    path(
        "reports/active-users/",
        views.admin_active_users,
        name="admin-reports-active-users",
    ),
]
