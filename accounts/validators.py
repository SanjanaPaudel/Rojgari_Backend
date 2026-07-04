import re

from rest_framework import serializers

from .models import PendingRegistration, User


def validate_nepal_phone(phone_number):
    """
    Accepts:
    +97798XXXXXXXX
    +97797XXXXXXXX
    98XXXXXXXX
    97XXXXXXXX

    Stores:
    +97798XXXXXXXX
    """

    phone_number = phone_number.strip()

    pattern = r"^(?:\+977)?9[78]\d{8}$"

    if not re.match(pattern, phone_number):
        raise serializers.ValidationError("Enter a valid Nepal phone number.")

    if phone_number.startswith("98") or phone_number.startswith("97"):
        phone_number = "+977" + phone_number

    return phone_number


def validate_strong_password(password):
    """
    Password must contain:
    - 8 characters
    - uppercase
    - lowercase
    - digit
    - special character
    """

    if len(password) < 8:
        raise serializers.ValidationError("Password must be at least 8 characters.")

    if not re.search(r"[A-Z]", password):
        raise serializers.ValidationError(
            "Password must contain at least one uppercase letter."
        )

    if not re.search(r"[a-z]", password):
        raise serializers.ValidationError(
            "Password must contain at least one lowercase letter."
        )

    if not re.search(r"\d", password):
        raise serializers.ValidationError("Password must contain at least one number.")

    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        raise serializers.ValidationError(
            "Password must contain at least one special character."
        )

    return password


def validate_unique_phone(phone_number):
    """
    Validate that the phone number is not already registered.
    Automatically remove expired pending registrations.
    """

    # User already registered
    if User.objects.filter(phone_number=phone_number).exists():
        raise serializers.ValidationError("Phone number is already registered.")

    # Check pending registration
    pending = PendingRegistration.objects.filter(phone_number=phone_number).first()

    if pending:
        # Delete expired pending registration automatically
        if pending.is_expired():
            pending.delete()

        else:
            raise serializers.ValidationError(
                "OTP verification is pending for this phone number."
            )

    return phone_number


def validate_unique_email(email):
    """
    Check if email already exists.
    """

    if email and User.objects.filter(email=email).exists():
        raise serializers.ValidationError("Email is already registered.")

    return email
