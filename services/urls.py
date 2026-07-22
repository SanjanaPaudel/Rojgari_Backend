from django.urls import path

from . import views

urlpatterns = [

    # Get the list of categories to show in user dashboard  /api/services/categories/
    path(
        "categories/", 
        views.get_categories, 
        name="get-categories"
    ),

    # Create the Booking record /api/services/bookings/
    path(
        "bookings/", 
        views.create_booking, 
        name="create-booking"
    ),

    # View the status of Booking : Pending, Accepted, Rejected, Expired  /api/services/bookings/38/status/
    path(
        "bookings/<int:booking_id>/status/", 
        views.booking_status, 
        name="booking-status"
    ),

    # Rate the Booking Services /api/services/bookings/38/rate/
    path(
        "bookings/<int:booking_id>/rate/", 
        views.rate_booking, 
        name="rate-booking"
    ),
]
