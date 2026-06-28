from django.contrib.auth.models import AbstractUser
from django.db import models

from accounts.managers import UserManager


class User(AbstractUser):
    objects = UserManager()
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("worker", "Worker"),
    )

    username = None

    phone_number = models.CharField(
        max_length=15,
        unique=True,
    )

    email = models.EmailField(
        unique=True,
        blank=True,
        null=True,
    )

    full_name = models.CharField(max_length=255)

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    USERNAME_FIELD = "phone_number"

    REQUIRED_FIELDS = ["full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class CustomerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    profile_photo = models.ImageField(
        upload_to="customers/profile/",
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.full_name


class WorkerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="worker_profile",
    )

    permanent_address = models.TextField()

    profile_photo = models.ImageField(upload_to="workers/profile/")

    citizenship_front = models.ImageField(upload_to="workers/citizenship/")

    citizenship_back = models.ImageField(upload_to="workers/citizenship/")

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name
