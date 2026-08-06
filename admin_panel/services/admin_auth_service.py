from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
from accounts.models import User


class AdminAuthService:
    @staticmethod
    def create_admin(validated_data):

        user = User.objects.create_user(
            phone_number=validated_data["phone_number"],
            full_name=validated_data["full_name"],
            email=validated_data["email"],
            password=validated_data["password"],
            role="admin",
        )

        user.is_staff = True
        user.is_superuser = True
        user.save()

        return {
            "message": "Admin created successfully.",
            "admin": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "email": user.email,
            },
        }


    @staticmethod
    def login(validated_data):

        email = validated_data["email"]
        password = validated_data["password"]

        user = User.objects.filter(email=email).first()

        if user is None:
            raise AuthenticationFailed("Invalid email or password.")

        if not user.check_password(password):
            raise AuthenticationFailed("Invalid email or password.")

        if user.role != "admin":
            raise AuthenticationFailed("You are not authorized.")

        return user