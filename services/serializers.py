from rest_framework import serializers

from accounts.models import Skill

from .models import Booking


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
