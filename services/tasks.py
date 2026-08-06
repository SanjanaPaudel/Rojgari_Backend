import logging 

from celery import shared_task
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import WorkerProfile
from services.matching import rank_candidates
from services.models import Booking, BookingOffer
from services.realtime import send_booking_offer, send_booking_update

from .models import Booking
from .offers import backfill
from .realtime import send_booking_update

logger = logging.getLogger(__name__)

STALE_BOOKING_MINUTES = 10
OFFER_EXPIRY_SECONDS = 120

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

@shared_task
def expire_stale_offers():
    cutoff = timezone.now() - timedelta(seconds=OFFER_EXPIRY_SECONDS)

    stale_offers = BookingOffer.objects.filter(
        status="pending",
        offered_at__lt=cutoff,
    ).select_related("booking")

    count = 0

    for offer in stale_offers:
        offer.status = "expired"
        offer.responded_at = timezone.now()
        offer.save()

        count +=1

        backfill(offer.booking)

    if count:
        logger.info(f"Expired {count} satle offer(s).")

    return count
