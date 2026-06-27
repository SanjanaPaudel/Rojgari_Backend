import uuid

from django.db import models


class Payment(models.Model):
    """
    Payment transaction associated with a Booking.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    booking = models.OneToOneField(
        "bookings.Booking", on_delete=models.CASCADE, related_name="payment"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(max_length=50)  # e.g., 'esewa', 'khalti', 'cod'
    status = models.CharField(
        max_length=50, default="pending"
    )  # pending, completed, failed
    transaction_ref = models.CharField(max_length=255, unique=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Payment {self.transaction_ref} - Status: {self.status}"
