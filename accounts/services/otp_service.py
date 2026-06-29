import random
from datetime import timedelta

from django.utils import timezone


class OTPService:

    OTP_LENGTH = 6

    OTP_EXPIRY_MINUTES = 3

    @staticmethod
    def generate_otp():

        return str(
            random.randint(100000, 999999)
        )

    @staticmethod
    def get_expiry_time():

        return (
            timezone.now()
            + timedelta(
                minutes=OTPService.OTP_EXPIRY_MINUTES
            )
        )
