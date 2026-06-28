from rest_framework import serializers
from .models import User

class CustomerSignupSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            "phone_number",
            "password",
            "confirm_password",
            "full_name",
            "email",
            "profile_photo",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "password": "Passwords do not match."
                }
            )

        return attrs
    

class WorkerSignupSerializer(serializers.ModelSerializer):

    confirm_password = serializers.CharField(
        write_only=True
    )

    citizenship = serializers.ImageField()

    class Meta:
        model = User

        fields = [
            "phone_number",
            "password",
            "confirm_password",
            "full_name",
            "email",
            "profile_photo",
            "citizenship",
        ]

        extra_kwargs = {
            "password": {
                "write_only": True
            }
        }

    def validate(self, attrs):

        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {
                    "password": "Passwords do not match."
                }
            )

        return attrs
    

