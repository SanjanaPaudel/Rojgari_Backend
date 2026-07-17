from rest_framework import serializers

from accounts.models import Skill

from .models import Booking, BookingOffer


class BookingCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(
        queryset=Skill.objects.filter(is_active=True),
    )

    class Meta:
        model = Booking
        fields = [
            "category",
            "description",
            "latitude",
            "longitude",
        ]

    def validate_description(self, value):
        if not value.strip():
            raise serializers.ValidationError("Description cannot be empty")

        return value


class WorkerSummarySerializer(serializers.Serializer):
    id = serializers.IntegerField()
    full_name = serializers.CharField(source="user.full_name")
    phone_number = serializers.CharField(source="user.phone_number")
    average_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    completed_jobs = serializers.IntegerField()
    current_latitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    current_longitude = serializers.DecimalField(max_digits=9, decimal_places=6)
    profile_photo = serializers.SerializerMethodField()

    def get_profile_photo(self, worker):
        request = self.context.get("request")

        if worker.profile_photo and request:
            return request.build_absolute_uri(worker.profile_photo.url)

        return None


class BookingDetailSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    worker = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "category",
            "description",
            "address_text",
            "latitude",
            "longitude",
            "status",
            "price",
            "rating",
            "created_at",
            "worker",
        ]

    def get_worker(self, booking):
        if not booking.worker:
            return None

        return WorkerSummarySerializer(booking.worker, context=self.context).data


class BookingOfferSerializer(serializers.ModelSerializer):
    worker_name = serializers.CharField(source="worker.user.full_name")

    class Meta:
        model = BookingOffer
        fields = [
            "id",
            "worker",
            "worker_name",
            "score",
            "status",
            "offered_at",
            "responded_at",
        ]


class RateBookingSerializer(serializers.Serializer):
    rating = serializers.DecimalField(
        max_digits=2, decimal_places=1, min_value=1, max_value=5
    )
