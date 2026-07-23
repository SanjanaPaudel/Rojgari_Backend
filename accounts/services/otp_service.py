import random
from datetime import timedelta

from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

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
    def send_otp(email, otp):
        """
        Send OTP to user's email.
        """

        subject = "Rojgari - Email Verification"

        message = f"""
    Hello,

    Thank you for registering with Rojgari.

    Your One-Time Password (OTP) is:

    {otp}

    This OTP is valid for 3 minutes.

    If you did not request this verification, please ignore this email.

    Regards,
    Rojgari Team
    """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

    @staticmethod
    def verify_otp(phone_number, otp):

        try:
            pending = PendingRegistration.objects.get(phone_number=phone_number)

        except PendingRegistration.DoesNotExist:
            return {"success": False, "message": "Registration not found."}

        if pending.is_expired():
            pending.delete()

            return {"success": False, "message": "OTP has expired."}

        #Check if the otp is correct 
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

        # The OTP is verified and then only this blocks runs; Create a row in User Table
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

        return {
            "success": True,
            "message": "Registration completed successfully. Please login to continue.",
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
            pending.email,
            otp,
        )

        return {
            "success": True,
            "message": "OTP sent successfully.",
            "expires_in": 180,
        }
