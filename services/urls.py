from django.urls import path

from . import views

urlpatterns = [
    path("categories/", views.get_categories, name="get-categories"),
    path("bookings/", views.create_booking, name="create-booking"),
    path(
        "bookings/<int:booking_id>/status/", views.booking_status, name="booking-status"
    ),
    path(
        "bookings/<int:booking_id>/complete/",
        views.complete_booking,
        name="complete-booking",
    ),
    path("bookings/<int:booking_id>/rate/", views.rate_booking, name="rate-booking"),
]
