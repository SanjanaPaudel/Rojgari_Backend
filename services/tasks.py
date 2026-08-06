import logging 

from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from .models import Booking
from .realtime import send_booking_update

logger = logging.getLogger(__name__)

STALE_BOOKING_MINUTES = 10

@shared_task
def expire_stale_bookings():
    cutoff = timezone.now() - timedelta(minutes=STALE_BOOKING_MINUTES)

    stale_bookings = Booking.objects.filter(
        status="active",
        created_at__lt=cutoff,
    ).exclude(
        offers__status="pending",
    )

    count = 0

    for booking in stale_bookings:
        booking.status = "cancelled"
        booking.save()

        send_booking_update(booking.id, {"status": "cancelled"})

        count += 1

    if count:
        logger.info(f"Auto-cancelled {count} stale bookings(s).")

    return count