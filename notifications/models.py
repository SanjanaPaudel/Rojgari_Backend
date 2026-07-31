from django.db import models

from accounts.models import User


# notification model
class DeviceToken(models.Model):
    DEVICE_CHOICES = (
        ("android", "Android"),
        ("ios", "iOS"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="device_tokens",
    )

    token = models.TextField(
        unique=True,
    )

    device_type = models.CharField(
        max_length=20,
        choices=DEVICE_CHOICES,
        default="android",
    )

    is_active = models.BooleanField(
        default=True,
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"{self.user.full_name} - {self.device_type}"

class Notification(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
    )

    title = models.CharField(max_length=255)

    body = models.TextField()

    notification_type = models.CharField(max_length=50)

    is_read = models.BooleanField(default=False)

    data = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.full_name} - {self.title}"