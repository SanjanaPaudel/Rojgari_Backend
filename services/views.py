from django.db import transaction
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.models import Skill, WorkerProfile
from accounts.permissions import IsCustomer
from accounts.serializers import SkillSerializer

from .geocoding import reverse_geocode
from .matching import rank_candidates
from .models import Booking, BookingMedia, BookingOffer
from .realtime import send_booking_offer, send_booking_update, send_offer_cancelled
from .serializers import (
    BookingCreateSerializer,
    BookingDetailSerializer,
    RateBookingSerializer,
)

NON_CANCELLABLE_STATUSES = ["completed", "cancelled"]


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsCustomer])
def get_categories(request):
    categories = Skill.objects.filter(is_active=True).order_by("display_order")

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
        top_candidates = ranked[:3]

        for worker, score in top_candidates:
            BookingOffer.objects.create(
                booking=booking,
                worker=worker,
                score=score,
                status="pending",
            )
            transaction.on_commit(
                lambda worker=worker, booking=booking: send_booking_offer(
                    worker.user_id,
                    {
                        "booking_id": booking.id,
                        "customer_name": request.user.full_name,
                        "service": booking.category.name,
                        "address": booking.address_text,
                        "description": booking.description,
                    },
                )
            )
            send_booking_offer(
                worker.user_id,
                {
                    "booking_id": booking.id,
                    "customer_name": request.user.full_name,
                    "service": booking.category.name,
                    "address": booking.address_text,
                    "description": booking.description,
                },
            )

    return Response(
        BookingDetailSerializer(booking, context={"request": request}).data,
        status=status.HTTP_201_CREATED,
    )


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
