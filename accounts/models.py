import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Core User model utilizing UUID as primary key.
    Subclasses AbstractUser to inherit default auth functionality.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=255, blank=True)
    phone_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    role = models.CharField(
        max_length=50, blank=True, null=True
    )  # e.g., 'worker', 'customer', 'admin'
    profile_photo_url = models.URLField(max_length=500, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Customer(models.Model):
    """
    Profile details specific to a Customer.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_profile"
    )
    address = models.CharField(max_length=255, blank=True, null=True)
    default_lat = models.FloatField(blank=True, null=True)
    default_lng = models.FloatField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Customer: {self.user.full_name or self.user.username}"


class Worker(models.Model):
    """
    Profile details specific to a Worker.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="worker_profile"
    )
    bio = models.TextField(blank=True, null=True)
    avg_rating = models.FloatField(default=0.0)
    total_jobs = models.IntegerField(default=0)
    is_available = models.BooleanField(default=True)
    is_approved = models.BooleanField(default=False)
    current_lat = models.FloatField(blank=True, null=True)
    current_lng = models.FloatField(blank=True, null=True)
    current_location = models.TextField(
        blank=True,
        null=True,
        help_text="Geometry representation (e.g., GeoJSON or WKT)",
    )
    bank_account = models.CharField(max_length=100, blank=True, null=True)
    wallet_number = models.CharField(max_length=100, blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Worker: {self.user.full_name or self.user.username}"


class WorkerDocument(models.Model):
    """
    Verification documents uploaded by a Worker.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(
        Worker, on_delete=models.CASCADE, related_name="documents"
    )
    document_type = models.CharField(max_length=100)  # e.g., 'citizenship', 'license'
    file_url = models.URLField(max_length=500)
    verification_status = models.CharField(
        max_length=50, default="pending"
    )  # pending, approved, rejected
    rejection_reason = models.TextField(blank=True, null=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.document_type} - {self.worker.user.username} ({self.verification_status})"
