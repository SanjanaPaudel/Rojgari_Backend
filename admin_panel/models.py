from django.conf import settings
from django.db import models

from accounts.models import WorkerProfile


class WorkerVerificationHistory(models.Model):
    ACTION_CHOICES = [
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("resubmission_requested", "Resubmission Requested"),
    ]

    worker = models.ForeignKey(
        WorkerProfile,
        on_delete=models.CASCADE,
        related_name="verification_history",
    )

    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="worker_verification_actions",
    )

    action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
    )

    note = models.TextField(
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"{self.worker.user.full_name} - "
            f"{self.action} by {self.admin}"
        )