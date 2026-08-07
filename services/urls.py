from django.urls import path

from . import views

urlpatterns = [
    # Get the list of categories to show in user dashboard  /api/services/categories/
    path("categories/", views.get_categories, name="get-categories"),
    # Create the Booking record /api/services/bookings/
    path("bookings/", views.create_booking, name="create-booking"),
    # View the status of Booking : Pending, Accepted, Rejected, Expired  /api/services/bookings/38/status/
    path(
        "bookings/<int:booking_id>/status/", views.booking_status, name="booking-status"
    ),
    # List all of teh customer's bookings, optionally filterd by ? status= /api/services/bookings/list/
    path("bookings/list/", views.booking_list, name="booking-list"),
    # Cancel Booking from customer side  /api/services/bookings/<id>/cancel/
    path(
        "bookings/<int:booking_id>/cancel/", views.cancel_booking, name="cancel-booking"
    ),
    # Rate the Booking Services /api/services/bookings/38/rate/
    path("bookings/<int:booking_id>/rate/", views.rate_booking, name="rate-booking"),
    # View The Message Endpoint
    path(
        "bookings/<int:booking_id>/messages/",
        views.message_list,
        name="message_list",
    ),
]
