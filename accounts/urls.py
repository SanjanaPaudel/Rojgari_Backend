from django.urls import path

from . import views

urlpatterns = [
    path(
        "signup/",
        views.signup,
        name="signup",
    ),
    # path(
    #     "worker/signup/",
    #     views.worker_signup,
    #     name="worker-signup",
    # ),

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
]
