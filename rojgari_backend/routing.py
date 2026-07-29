
from django.urls import re_path

from accounts.consumers import WorkerOfferConsumer
from services.consumers import BookingStatusConsumer

websocket_urlpatterns = [
    re_path(r"^ws/worker/offers/$", WorkerOfferConsumer.as_asgi()),
    re_path(r"^ws/bookings/(?P<booking_id>\d+)/$", BookingStatusConsumer.as_asgi()),
]
