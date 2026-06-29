from rest_framework import serializers

from .validators import (
    validate_nepal_phone,
    validate_strong_password,
    validate_unique_email,
    validate_unique_phone,
)


class BaseSignupSerializer(serializers.Serializer):

    full_name = serializers.CharField(
        max_length=255,
    )

    phone_number = serializers.CharField(
        max_length=14,
        validators=[
            validate_nepal_phone,
            validate_unique_phone,
        ],
    )

    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_strong_password,
        ],
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "confirm_password": "Passwords do not match."
                }
            )

        return attrs

class CustomerSignupSerializer(BaseSignupSerializer):

    email = serializers.EmailField(
    required=False,
    allow_null=True,
    allow_blank=True,
    validators=[
        validate_unique_email,
    ],
    )

    profile_photo = serializers.ImageField(
        required=False,
    )

class WorkerSignupSerializer(BaseSignupSerializer):

    email = serializers.EmailField(
    required=False,
    allow_null=True,
    allow_blank=True,
    validators=[
        validate_unique_email,
    ],
    )

    permanent_address = serializers.CharField()

    profile_photo = serializers.ImageField()

    citizenship_front = serializers.ImageField()

    citizenship_back = serializers.ImageField()

