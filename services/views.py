from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from accounts.models import Skill
from accounts.permissions import IsCustomer
from accounts.serializers import SkillSerializer

from .geocoding import reverse_geocode
from .matching import rank_candidates
from .models import Booking, BookingMedia, BookingOffer
from .serializers import BookingCreateSerializer


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

    return Response(
        {
            "id": booking.id,
            "category": booking.category.name,
            "description": booking.description,
            "address_text": booking.address_text,
            "status": booking.status,
            "offers_sent": len(top_candidates),
        },
        status=status.HTTP_201_CREATED,
    )