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
]
