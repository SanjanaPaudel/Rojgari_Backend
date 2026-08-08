from rest_framework import serializers

from accounts.models import Skill
from services.models import Booking


class AdminLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class CreateAdminSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs


class DashboardSerializer(serializers.Serializer):
    workers = serializers.DictField()
    bookings = serializers.DictField()
    skills = serializers.DictField()


class CategorySerializer(serializers.ModelSerializer):
    total_workers = serializers.IntegerField(
        source="workers.count",
        read_only=True,
    )

    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "icon",
            "description",
            "is_active",
            "display_order",
            "total_workers",
        ]
        read_only_fields = [
            "id",
            "total_workers",
        ]


class AdminProfileSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)

    full_name = serializers.CharField(
        max_length=255,
        required=False,
    )

    phone_number = serializers.CharField(
        max_length=15,
        required=False,
    )

    email = serializers.EmailField(
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    profile_photo = serializers.CharField(
        read_only=True,
        allow_null=True,
    )


class AdminProfilePhotoSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField(
        required=True,
    )


class AdminChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(
        write_only=True,
    )

    new_password = serializers.CharField(
        write_only=True,
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs

class AdminBookingDetailSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.user.full_name")
    customer_phone = serializers.CharField(source="customer.user.phone_number")
    customer_email = serializers.CharField(source="customer.user.email")
    worker_name = serializers.CharField(source="worker.user.full_name", default=None)
    worker_phone = serializers.CharField(source="worker.user.phone_number", default=None)
    worker_email = serializers.CharField(source="worker.user.email", default=None)
    category_name = serializers.CharField(source="category.name")
    media = serializers.SerializerMethodField()
    timeline = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "category_name",
            "status",
            "description",
            "address_text",
            "latitude",
            "longitude",
            "created_at",
            "customer_name",
            "customer_phone",
            "customer_email",
            "worker_name",
            "worker_phone",
            "worker_email",
            "media",
            "timeline",
        ]

    def get_media(self, booking):
        request = self.context.get("request")
        return [
            {
                "url": request.build_absolute_uri(m.file.url) if request else m.file.url,
                "type": m.media_type,
            }
            for m in booking.media.all()
        ]

    def get_timeline(self, booking):
        return [
            {"status": h.status, "changed_at": h.changed_at}
            for h in booking.status_history.all()
        ]

class AdminBookingListSerializer(serializers.ModelSerializer):
    customer_name = serializers.CharField(source="customer.user.full_name")
    customer_phone = serializers.CharField(source="customer.user.phone_number")
    worker_name = serializers.CharField(
        source="worker.user.full_name", default=None
    )
    worker_phone = serializers.CharField(
        source="worker.user.phone_number", default=None
    )
    category_name = serializers.CharField(source="category.name")

    class Meta:
        model = Booking
        fields = [
            "id",
            "customer_name",
            "customer_phone",
            "worker_name",
            "worker_phone",
            "category_name",
            "status",
            "created_at",
        ]
