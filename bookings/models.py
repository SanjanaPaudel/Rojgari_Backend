import uuid

from django.db import models


class Booking(models.Model):
    """
    A match between a ServiceRequest and a Worker.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    request = models.ForeignKey(
        "services.ServiceRequest", on_delete=models.CASCADE, related_name="bookings"
    )
    worker = models.ForeignKey(
        "accounts.Worker", on_delete=models.CASCADE, related_name="bookings"
    )
    status = models.CharField(
        max_length=50, default="accepted"
    )  # accepted, started, completed, cancelled
    agreed_price = models.DecimalField(max_digits=10, decimal_places=2)
    accepted_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(blank=True, null=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    cancelled_at = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Booking for {self.request.category.name} - Worker: {self.worker.user.username}"


class Review(models.Model):
    """
    Review and rating submitted post-booking completion.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.ForeignKey(
        Booking, on_delete=models.CASCADE, related_name="reviews"
    )
    reviewer = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="submitted_reviews"
    )
    reviewee = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="received_reviews"
    )
    rating = models.IntegerField()  # 1 to 5
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.reviewer.username} to {self.reviewee.username} ({self.rating}★)"


class WorkerLocationHistory(models.Model):
    """
    Geographical tracking breadcrumbs for Workers.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    worker = models.ForeignKey(
        "accounts.Worker", on_delete=models.CASCADE, related_name="location_history"
    )
    lat = models.FloatField()
    lng = models.FloatField()
    location = models.TextField(
        blank=True,
        null=True,
        help_text="Geometry representation (e.g., GeoJSON or WKT)",
    )
    recorded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"History of {self.worker.user.username} at {self.recorded_at}"
