from accounts.models import CustomerProfile, User, WorkerProfile
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed
# from accounts.models import CustomerProfile, User, WorkerProfile
from django.contrib.auth.hashers import make_password
from accounts.models import PendingRegistration
from accounts.services.otp_service import OTPService


class AuthService:
    @staticmethod
    def create_user_registration(validated_data):

        validated_data.pop("confirm_password")

        otp = OTPService.generate_otp()

        expires_at = OTPService.get_expiry_time()

        PendingRegistration.objects.filter(
            phone_number=validated_data["phone_number"]
        ).delete()

        PendingRegistration.objects.create(
            role=validated_data["role"],
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            email=validated_data.get("email"),
            password=make_password(validated_data["password"]),
            profile_photo=validated_data.get("profile_photo"),
            otp=otp,
            expires_at=expires_at,
        )

        OTPService.send_otp(
            validated_data["phone_number"],
            otp,
        )
        return {
            "message": "OTP sent successfully.",
            "expires_in": 180,
        }
    
    @staticmethod
    def create_worker(validated_data):
        validated_data.pop("confirm_password")

        profile_photo = validated_data.pop("profile_photo")
        citizenship_front = validated_data.pop("citizenship_front")
        citizenship_back = validated_data.pop("citizenship_back")
        permanent_address = validated_data.pop("permanent_address")

        user = User.objects.create_user(
            full_name=validated_data["full_name"],
            phone_number=validated_data["phone_number"],
            email=validated_data["email"],
            password=validated_data["password"],
            role="worker",
        )

        WorkerProfile.objects.create(
            user=user,
            permanent_address=permanent_address,
            profile_photo=profile_photo,
            citizenship_front=citizenship_front,
            citizenship_back=citizenship_back,
        )

        return user

    @staticmethod
    def login(validated_data):
        phone_number = validated_data["phone_number"]
        password = validated_data["password"]

        user = authenticate(phone_number=phone_number, password=password)

        if user is None:
            raise AuthenticationFailed("Invalid phone number or password.")

        return user