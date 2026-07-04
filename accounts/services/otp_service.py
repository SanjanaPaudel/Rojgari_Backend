import random
from datetime import timedelta

from django.utils import timezone
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import (
    CustomerProfile,
    PendingRegistration,
    User,
    WorkerProfile,
)


class OTPService:
    OTP_LENGTH = 6

    OTP_EXPIRY_MINUTES = 3

    @staticmethod
    def generate_otp():

        return str(random.randint(100000, 999999))

    @staticmethod
    def get_expiry_time():

        return timezone.now() + timedelta(minutes=OTPService.OTP_EXPIRY_MINUTES)

    @staticmethod
    def send_otp(phone_number, otp):
        """
        Development OTP sender.
        Prints OTP to terminal.
        """

        print("\n" + "=" * 50)
        print("ROJGARI OTP")
        print("=" * 50)
        print(f"Phone Number : {phone_number}")
        print(f"OTP          : {otp}")
        print(f"Expires In   : {OTPService.OTP_EXPIRY_MINUTES} minutes")
        print("=" * 50 + "\n")

    @staticmethod
    def verify_otp(phone_number, otp):

        try:
            pending = PendingRegistration.objects.get(phone_number=phone_number)

        except PendingRegistration.DoesNotExist:
            return {"success": False, "message": "Registration not found."}

        if pending.is_expired():
            pending.delete()

            return {"success": False, "message": "OTP has expired."}

        if pending.otp != otp:
            pending.attempts += 1
            pending.save()

            if pending.attempts >= 3:
                pending.delete()

                return {"success": False, "message": "Maximum OTP attempts exceeded."}

            return {
                "success": False,
                "message": f"Invalid OTP. Remaining attempts: {3 - pending.attempts}",
            }

        user = User.objects.create(
            full_name=pending.full_name,
            phone_number=pending.phone_number,
            email=pending.email,
            password=pending.password,
            role=pending.role,
        )

        if pending.role == "customer":
            CustomerProfile.objects.create(
                user=user,
                profile_photo=pending.profile_photo,
            )

        else:
            WorkerProfile.objects.create(
                user=user,
                profile_photo=pending.profile_photo,
            )

        pending.delete()

        refresh = RefreshToken.for_user(user)

        return {
            "success": True,
            "message": "Registration completed successfully.",
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "email": user.email,
                "role": user.role,
            },
            "tokens": {
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
        }

    @staticmethod
    def resend_otp(phone_number):

        try:
            pending = PendingRegistration.objects.get(phone_number=phone_number)

        except PendingRegistration.DoesNotExist:
            return {"success": False, "message": "Registration not found."}

        if not pending.is_expired():
            remaining = int((pending.expires_at - timezone.now()).total_seconds())

            return {
                "success": False,
                "message": "Please wait before requesting another OTP.",
                "remaining_seconds": remaining,
            }

        otp = OTPService.generate_otp()

        pending.otp = otp
        pending.expires_at = OTPService.get_expiry_time()
        pending.attempts = 0

        pending.save()

        OTPService.send_otp(
            pending.phone_number,
            otp,
        )

        return {
            "success": True,
            "message": "OTP sent successfully.",
            "expires_in": 180,
        }
