from django.urls import path

from . import views

urlpatterns = [
    path(
        "categories/",
        views.get_categories,
        name="get-categories"
    ),
    path(
        "bookings/",
        views.create_booking, 
        name="create-booking"
    )
]

