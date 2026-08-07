from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from accounts.models import PasswordResetOTP, User
from accounts.services.otp_service import OTPService


class PasswordResetService:
    @staticmethod
    def _send_reset_otp(email, otp):
        subject = "Rojgari - Reset Your Password"
        message = f"""
    Hello,

    We received a request to reset the password for your Rojgari account.

    Your One-Time Password (OTP) is:

    {otp}

    This OTP is valid for 3 minutes.

    If you did not request a password reset, please ignore this email
    and your password will remain unchanged.

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
    def request_reset(email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {"success": False, "message": "No account found with email address"}

        otp = OTPService.generate_otp()
        expires_at = OTPService.get_expiry_time()

        # Only one active reset request per user at a time - calling this twice just replaces the old OTP.
        PasswordResetOTP.objects.filter(user=user).delete()

        PasswordResetOTP.objects.create(
            user=user,
            otp=otp,
            expires_at=expires_at,
        )

        PasswordResetService._send_reset_otp(email, otp)

        return {
            "success": True,
            "message": "OTP sent successfully to you email.",
            "expires_in": 180,
        }

    @staticmethod
    def resend_otp(email):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {
                "success": False,
                "message": "No account found with this email address.",
            }

        reset_request = PasswordResetOTP.objects.filter(user=user).first()
        if not reset_request:
            return {"success": False, "message": "No pending password reset request"}

        if not reset_request.is_expired():
            remaining = int((reset_request.expires_at - timezone.now()).total_seconds())
            return {
                "success": False,
                "message": "Please wait before requesting another OTP.",
                "remaining_seconds": remaining,
            }

        otp = OTPService.generate_otp()
        reset_request.otp = otp
        reset_request.expires_at = OTPService.get_expiry_time()
        reset_request.attempts = 0
        reset_request.is_verified = False
        reset_request.save()

        PasswordResetService._send_reset_otp(email, otp)

        return {
            "success": True,
            "message": "OTP sent successfully to your email.",
            "expires_in": 180,
        }

    @staticmethod
    def verify_otp(email, otp):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {
                "success": False,
                "message": "No account found with this email address.",
            }

        reset_request = PasswordResetOTP.objects.filter(user=user).first()
        if not reset_request:
            return {
                "success": False,
                "message": "No pending password reset request found. Please start again.",
            }

        if reset_request.is_expired():
            reset_request.delete()
            return {"success": False, "message": "OTP has expired."}

        if reset_request.otp != otp:
            reset_request.attempts += 1
            reset_request.save()

            if reset_request.attempts >= 3:
                reset_request.delete()
                return {
                    "success": False,
                    "message": "Maximum OTP attempts exceeded. Please start again.",
                }

            return {
                "success": False,
                "message": f"Invalid OTP. Remaining attempts: {3 - reset_request.attempts}",
            }

        reset_request.is_verified = True
        reset_request.save()

        return {
            "success": True,
            "message": "OTP verified successfully. You can now set a new password.",
        }

    @staticmethod
    def reset_password(email, new_password):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return {
                "success": False,
                "message": "No account found with this email address.",
            }

        reset_request = PasswordResetOTP.objects.filter(user=user).first()
        if not reset_request:
            return {
                "success": False,
                "message": "No pending password reset request found. Please start again.",
            }

        if reset_request.is_expired():
            reset_request.delete()
            return {
                "success": False,
                "message": "Your OTP has expired. Please start again.",
            }

        if not reset_request.is_verified:
            return {
                "success": False,
                "message": "Please verify the OTP before setting a new password.",
            }

        user.set_password(new_password)
        user.save(update_fields=["password"])

        reset_request.delete()

        return {
            "success": True,
            "message": "Password reset successfully. Please login with your new password.",
        }
