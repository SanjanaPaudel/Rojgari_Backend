from django.urls import path

from . import views

urlpatterns = [
    path("login/", views.admin_login),
    path("create/", views.create_admin),
    path("verify-otp/",views.verify_admin_otp,),
    path("dashboard/",views.dashboard,),
    path("workers/pending/",views.pending_workers,),
    path("workers/<int:worker_id>/",views.worker_details,),
]
