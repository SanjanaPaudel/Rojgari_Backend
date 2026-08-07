from rest_framework import serializers

from accounts.models import Skill


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
