from django.db import transaction
from django.db.models import Q
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Skill, WorkerProfile
from accounts.permissions import IsCustomer
from accounts.serializers import SkillSerializer
from services.matching import distance_km
from services.pricing_service import PricingService
from .geocoding import reverse_geocode
from .matching import rank_candidates
from .models import Booking, BookingMedia, BookingOffer
from .offers import OFFER_EXPIRY_SECONDS
from .realtime import send_booking_offer, send_booking_update, send_offer_cancelled
from .serializers import (
    BookingCreateSerializer,
    BookingDetailSerializer,
    BookingListSerializer,
    MessageSerializer,
    RateBookingSerializer,
)

MAX_INITIAL_OFFERS = 3
NON_CANCELLABLE_STATUSES = ["completed", "cancelled"]


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def get_categories(request):
    categories = Skill.objects.filter(is_active=True).order_by(
        "display_order",
        "id",
    )

    serializer = SkillSerializer(categories, many=True)

    return Response({"categories": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsCustomer])
def create_booking(request):
    serializer = BookingCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    photos = request.FILES.getlist("photos")
    video = request.FILES.get("video")

    if len(photos) > 3:
        return Response(
            {"photos": "You can upload a maximum of 3 photos."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    latitude = serializer.validated_data["latitude"]
    longitude = serializer.validated_data["longitude"]

    address_text = reverse_geocode(latitude, longitude)

    with transaction.atomic():
        booking = Booking.objects.create(
            customer=request.user.customer_profile,
            category=serializer.validated_data["category"],
            description=serializer.validated_data["description"],
            latitude=latitude,
            longitude=longitude,
            address_text=address_text,
            status="active",
        )

        for photo in photos:
            BookingMedia.objects.create(
                booking=booking,
                file=photo,
                media_type="photo",
            )

        if video:
            BookingMedia.objects.create(
                booking=booking,
                file=video,
                media_type="video",
            )

        ranked = rank_candidates(booking)

        offers_created = 0

        for worker, score in ranked:
            # Stop once we've successfully sent out enough offers - not just after checking the first 3 candidates.

            if offers_created >= MAX_INITIAL_OFFERS:
                break

            distance = distance_km(
                booking.latitude,
                booking.longitude,
                worker.current_latitude,
                worker.current_longitude,
            )

            pricing = PricingService.calculate_visit_charge(distance)

            # Skip workers outside the configured service radius - keep checking further candidates instead of giving up
            if not pricing["success"]:
                continue

            new_offer = BookingOffer.objects.create(
                booking=booking,
                worker=worker,
                score=score,
                visit_charge=pricing["visit_charge"],
                status="pending",
            )

            offers_created += 1

            transaction.on_commit(
                lambda worker=worker, booking=booking, new_offer=new_offer: (
                    send_booking_offer(
                        worker.user_id,
                        {
                            "offer_id": new_offer.id,
                            "booking_id": booking.id,
                            "customer_name": request.user.full_name,
                            "service": booking.category.name,
                            "address": booking.address_text,
                            "description": booking.description,
                            "visit_charge": float(new_offer.visit_charge),
                            "expires_in_seconds": OFFER_EXPIRY_SECONDS,
                        },
                    )
                )
            )

    return Response(
        BookingDetailSerializer(booking, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def booking_list(request):
    bookings = Booking.objects.filter(customer=request.user.customer_profile)

    status_filter = request.query_params.get("status")

    if status_filter:
        bookings = bookings.filter(status=status_filter)

    bookings = bookings.order_by("-created_at")

    serializer = BookingListSerializer(
        bookings, many=True, context={"request": request}
    )

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def booking_status(request, booking_id):
    try:
        booking = Booking.objects.get(
            id=booking_id, customer=request.user.customer_profile
        )
    except Booking.DoesNotExist:
        return Response(
            {"detail": "Booking not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(BookingDetailSerializer(booking, context={"request": request}).data)


# Cancel request from customer side
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsCustomer])
def cancel_booking(request, booking_id):
    try:
        booking = Booking.objects.get(
            id=booking_id, customer=request.user.customer_profile
        )
    except Booking.DoesNotExist:
        return Response(
            {"detail": "Booking not found."},
            status=status.HTTP_404_NOT_FOUND,
        )
    if booking.status in NON_CANCELLABLE_STATUSES:
        return Response(
            {"detail": "This booking can no longer be cancelled"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    pending_offers = list(
        booking.offers.filter(status="pending").values("id", "worker__user_id")
    )

    with transaction.atomic():
        booking.status = "cancelled"
        booking.save()

        booking.offers.filter(status__in=["pending", "accepted"]).update(
            status="cancelled"
        )

    for offer in pending_offers:
        send_offer_cancelled(offer["worker__user_id"], offer["id"])

    send_booking_update(booking.id, {"status": "cancelled"})

    return Response({"details": "Booking cancelled successfully."})


# Rate Booking by Customer
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsCustomer])
def rate_booking(request, booking_id):
    try:
        booking = Booking.objects.get(
            id=booking_id, customer=request.user.customer_profile
        )
    except Booking.DoesNotExist:
        return Response(
            {"detail": "Booking not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if booking.status != "completed":
        return Response(
            {"detail": "Only completed bookings can be rated."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if booking.rating is not None:
        return Response(
            {"detail": "This booking has already been rated."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    serializer = RateBookingSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    new_rating = serializer.validated_data["rating"]

    with transaction.atomic():
        booking.rating = new_rating
        booking.review_text = serializer.validated_data.get("review_text", "")
        booking.save()

        worker = WorkerProfile.objects.select_for_update().get(id=booking.worker_id)

        total = worker.total_reviews
        current_average = worker.average_rating

        new_average = ((current_average * total) + new_rating) / (total + 1)

        worker.average_rating = round(new_average, 2)
        worker.total_reviews = total + 1
        worker.save()

    return Response(BookingDetailSerializer(booking, context={"request": request}).data)


# Message View Function


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def message_list(request, booking_id):
    try:
        booking = Booking.objects.get(
            Q(id=booking_id),
            Q(customer__user=request.user) | Q(worker__user=request.user),
        )
    except Booking.DoesNotExist:
        return Response(
            {"detail": "Booking not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    messages = list(booking.messages.order_by("-created_at")[:100])
    messages.reverse()

    serializer = MessageSerializer(messages, many=True)
    data = serializer.data

    booking.messages.exclude(sender=request.user).filter(is_read=False).update(
        is_read=True
    )

    return Response(data)
