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

    @staticmethod
    def get_profile(user):
        return {
            "id": user.id,
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "profile_photo": (
                user.profile_photo.url
                if user.profile_photo
                else None
            ),
        }

    @staticmethod
    def update_profile(user, validated_data):
        email_change_requested = "email" in validated_data

        if "full_name" in validated_data:
            user.full_name = validated_data["full_name"]

        if "phone_number" in validated_data:
            user.phone_number = validated_data["phone_number"]

        user.save()

        profile = AdminAuthService.get_profile(user)

        if email_change_requested:
            return {
                "message": "Profile updated successfully. Email address cannot be changed.",
                "profile": profile,
            }

        return {
            "message": "Profile updated successfully.",
            "profile": profile,
        }

    @staticmethod
    def update_profile_photo(user, profile_photo):
        profile = user.admin_profile

        profile.profile_photo = profile_photo
        profile.save()

        return {
            "message": "Profile photo updated successfully.",
            "profile_photo": profile.profile_photo.url,
        }

    @staticmethod
    def change_password(user, validated_data):
        old_password = validated_data["old_password"]
        new_password = validated_data["new_password"]

        if not user.check_password(old_password):
            return {
                "success": False,
                "field": "old_password",
                "message": "Old password is incorrect.",
            }

        user.set_password(new_password)
        user.save()

        return {
            "success": True,
            "message": "Password changed successfully.",
        }
