from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

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


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.ImageField(
        upload_to="skills/icons/",
        blank=True,
        null=True,
    )
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0)
    def __str__(self):
        return self.name


class WorkerProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )

    permanent_address = models.TextField(
        blank=True,
        default="",
    )

    profile_photo = models.ImageField(
        upload_to="profile_photos/",
        blank=True,
        null=True,
    )

    citizenship_front = models.ImageField(
        upload_to="citizenship/front/",
        blank=True,
        null=True,
    )

    citizenship_back = models.ImageField(
        upload_to="citizenship/back/",
        blank=True,
        null=True,
    )

    skills = models.ManyToManyField(
        Skill,
        blank=True,
        related_name="workers",
    )

    has_selected_skills = models.BooleanField(
        default=False,
    )

    # NEW
    years_of_experience = models.PositiveIntegerField(default=0)

    is_online = models.BooleanField(default=False)

    completed_jobs = models.PositiveIntegerField(default=0)

    average_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
    )

    total_reviews = models.PositiveIntegerField(default=0)

    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.full_name


class PendingRegistration(models.Model):
    ROLE_CHOICES = (
        ("customer", "Customer"),
        ("worker", "Worker"),
    )

    full_name = models.CharField(max_length=255)

    phone_number = models.CharField(
        max_length=14,
        unique=True,
    )

    email = models.EmailField(
        blank=True,
        null=True,
    )

    password = models.CharField(
        max_length=128,
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
    )

    permanent_address = models.TextField(
        blank=True,
        null=True,
    )

    profile_photo = models.ImageField(
        upload_to="pending/profile/",
        blank=True,
        null=True,
    )

    citizenship_front = models.ImageField(
        upload_to="pending/citizenship/",
        blank=True,
        null=True,
    )

    citizenship_back = models.ImageField(
        upload_to="pending/citizenship/",
        blank=True,
        null=True,
    )

    otp = models.CharField(max_length=6)

    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.expires_at

    def __str__(self):
        return self.phone_number
