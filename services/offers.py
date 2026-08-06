from django.db import transaction

from .matching import distance_km, rank_candidates
from .models import BookingOffer
from .pricing_service import PricingService
from .realtime import send_booking_offer

OFFER_EXPIRY_SECONDS = 120


def backfill(booking):
    """
    Find the next-best candidate (within service radius) not already
    offered this booking, and create a fresh pending offer for them.
    """
    already_offered_ids = list(
        BookingOffer.objects.filter(booking=booking).values_list(
            "worker_id", flat=True
        )
    )

    ranked = rank_candidates(booking, exclude_worker_ids=already_offered_ids)

    for worker, score in ranked:
        distance = distance_km(
            booking.latitude,
            booking.longitude,
            worker.current_latitude,
            worker.current_longitude,
        )

        pricing = PricingService.calculate_visit_charge(distance)

        if not pricing["success"]:
            continue

        new_offer = BookingOffer.objects.create(
            booking=booking,
            worker=worker,
            score=score,
            visit_charge=pricing["visit_charge"],
            status="pending",
        )

        transaction.on_commit(
            lambda worker=worker, new_offer=new_offer: send_booking_offer(
                worker.user_id,
                {
                    "offer_id": new_offer.id,
                    "booking_id": booking.id,
                    "customer_name": booking.customer.user.full_name,
                    "service": booking.category.name,
                    "address": booking.address_text,
                    "description": booking.description,
                    "visit_charge": float(new_offer.visit_charge),
                    "expires_in_seconds": OFFER_EXPIRY_SECONDS,
                },
            )
        )

        return new_offer

    return None