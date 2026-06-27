import uuid

from django.core.cache import cache
from django.db import models


class ServiceCategory(models.Model):
    """
    Job classification categories (e.g., Plumbing, Electrician, Cleaning).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    icon_url = models.URLField(max_length=500, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        # Clear the active categories cache key to prevent serving stale data
        cache.delete("active_service_categories")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Clear the active categories cache key on delete
        cache.delete("active_service_categories")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.name


class WorkerService(models.Model):
    """
    Mapping table linking Workers to the ServiceCategories they provide.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(
        "accounts.Worker", on_delete=models.CASCADE, related_name="offered_services"
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="workers"
    )
    years_experience = models.IntegerField(default=0)
    skill_level = models.CharField(
        max_length=50, blank=True, null=True
    )  # e.g., Beginner, Intermediate, Expert
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.worker.user.username} - {self.category.name}"


class ServiceRequest(models.Model):
    """
    A service request posted by a Customer looking for help.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(
        "accounts.Customer", on_delete=models.CASCADE, related_name="requests"
    )
    category = models.ForeignKey(
        ServiceCategory, on_delete=models.CASCADE, related_name="requests"
    )
    description = models.TextField()
    status = models.CharField(
        max_length=50, default="pending"
    )  # pending, accepted, completed, cancelled, expired
    customer_lat = models.FloatField()
    customer_lng = models.FloatField()
    customer_location = models.TextField(
        blank=True,
        null=True,
        help_text="Geometry representation (e.g., GeoJSON or WKT)",
    )
    address = models.CharField(max_length=255)
    requested_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Request {self.category.name} by {self.customer.user.username}"
