from rest_framework import serializers


class CustomerSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)
    phone_number = serializers.CharField(max_length=15)

    email = serializers.EmailField(
        required=False,
        allow_null=True,
        allow_blank=True,
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    profile_photo = serializers.ImageField(
        required=False,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs


class WorkerSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(max_length=255)

    phone_number = serializers.CharField(max_length=15)

    email = serializers.EmailField()

    permanent_address = serializers.CharField()

    password = serializers.CharField(
        write_only=True,
        min_length=8,
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    profile_photo = serializers.ImageField()

    citizenship_front = serializers.ImageField()

    citizenship_back = serializers.ImageField()

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs
