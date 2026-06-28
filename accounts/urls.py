from django.urls import path

from accounts.views import (
    customer_signup,
    worker_signup,
)

urlpatterns = [
    path(
        "signup/customer/",
        customer_signup,
        name="customer-signup",
    ),
    path(
        "signup/worker/",
        worker_signup,
        name="worker-signup",
    ),
]
