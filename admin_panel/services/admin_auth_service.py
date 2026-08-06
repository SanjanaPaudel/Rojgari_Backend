from rest_framework.exceptions import AuthenticationFailed

from accounts.models import User
from accounts.services.auth_service import AuthService


class AdminAuthService:
    @staticmethod
    def create_admin(validated_data):

        validated_data["role"] = "admin"

        return AuthService.create_user_registration(validated_data)

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

        # NEW
        if not user.is_active:
            raise AuthenticationFailed("Please verify your email before logging in.")

        return user
