# Create your models here.
from django.db import models

from accounts.models import CustomerProfile, Skill, User, WorkerProfile


class Booking(models.Model):
    # Single lifecycle field covering both matching and on-site work progress:
    # active (searching for a worker) -> assigned (worker accepted) ->
    # working (worker started) -> completed / cancelled.
    # "scheduled" is reserved for the not-yet-implemented scheduled-booking flow.
    STATUS_CHOICES = [
        ("active", "Active"),
        ("scheduled", "Scheduled"),
        ("assigned", "Assigned"),
        ("working", "Working"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
    ]

    customer = models.ForeignKey(
        CustomerProfile,
        on_delete=models.CASCADE,
        related_name="bookings",
    )

    worker = models.ForeignKey(
        WorkerProfile,
        on_delete=models.SET_NULL,
        related_name="bookings",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        Skill,
        on_delete=models.PROTECT,
        related_name="bookings",
    )

    description = models.CharField(max_length=300)

    latitude = models.DecimalField(max_digits=9, decimal_places=6)

    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    address_text = models.CharField(max_length=500, blank=True, null=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="active",
    )

    scheduled_time = models.DateTimeField(null=True, blank=True)

    rating = models.DecimalField(max_digits=2, decimal_places=1, null=True, blank=True)

    review_text = models.TextField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.category.name} booking by {self.customer.user.full_name}"


class BookingMedia(models.Model):
    MEDIA_TYPE_CHOICES = [
        ("photo", "Photo"),
        ("video", "Video"),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="media",
    )

    file = models.FileField(upload_to="booking_media/")

    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPE_CHOICES,
    )

    def __str__(self):
        return f"{self.media_type} for booking #{self.booking_id}"


class BookingOffer(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("accepted", "Accepted"),
        ("rejected", "Rejected"),
        ("expired", "Expired"),
        ("cancelled", "Cancelled"),
    ]

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="offers",
    )

    worker = models.ForeignKey(
        WorkerProfile,
        on_delete=models.CASCADE,
        related_name="booking_offers",
    )

    score = models.DecimalField(max_digits=4, decimal_places=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    offered_at = models.DateTimeField(auto_now_add=True)

    responded_at = models.DateTimeField(null=True, blank=True)

    visit_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0.00,
    )

    def __str__(self):
        return f"Offer for booking #{self.booking_id} to {self.worker.user.full_name}"


class PricingConfiguration(models.Model):
    price_per_km = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=100.00,
    )

    minimum_visit_charge = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=100.00,
    )

    maximum_service_radius = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=5.00,
        help_text="Maximum distance (KM) to search nearby workers.",
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    @classmethod
    def get_config(cls):
        config = cls.objects.first()

        if not config:
            config = cls.objects.create()

        return config

    def __str__(self):
        return "Pricing Configuration"


class Message(models.Model):
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="sent_message",
    )

    content = models.TextField(max_length=2000)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender.full_name} on booking #{self.booking_id}"
