from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Customer"
        WORKER = "worker", "Worker"

    username = None

    phone_number = models.CharField(
        max_length=15,
        unique=True,
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    full_name = models.CharField(
        max_length=150,
    )

    email = models.EmailField(
        unique=True,
    )

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    is_phone_verified = models.BooleanField(
        default=False,
    )

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = [
        "email",
        "full_name",
    ]

    def __str__(self):
        return f"{self.full_name} ({self.phone_number})"


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    def __str__(self):
        return self.user.full_name


class WorkerProfile(models.Model):
    class VerificationStatus(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="worker_profile",
    )

    citizenship_image = models.ImageField(
        upload_to="citizenship/",
    )

    verification_status = models.CharField(
        max_length=20,
        choices=VerificationStatus.choices,
        default=VerificationStatus.PENDING,
    )

    def __str__(self):
        return self.user.full_name
