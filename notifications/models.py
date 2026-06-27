import uuid

from django.db import models


class Notification(models.Model):
    """
    System alert notification delivered to Users.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="notifications"
    )
    title = models.CharField(max_length=255)
    body = models.TextField()
    type = models.CharField(max_length=50)  # e.g., 'booking_update', 'payment_success'
    is_read = models.BooleanField(default=False)
    reference_id = models.UUIDField(blank=True, null=True)
    reference_type = models.CharField(
        max_length=100, blank=True, null=True
    )  # e.g., 'Booking', 'Payment'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user.username}: {self.title}"
