from uuid import UUID

from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import ErrorSchema, NotificationOut
from notifications.models import Notification

router = Router()


@router.get("", auth=django_auth, response=list[NotificationOut])
def list_notifications(request):
    """
    Retrieve all in-app notifications for current authenticated user.
    """
    return list(Notification.objects.filter(user=request.user).order_by("-created_at"))


@router.post(
    "/{notification_id}/read",
    auth=django_auth,
    response={200: NotificationOut, 400: ErrorSchema},
)
def mark_notification_read(request, notification_id: UUID):
    """
    Mark a notification as read.
    """
    notification = get_object_or_404(
        Notification, id=notification_id, user=request.user
    )
    notification.is_read = True
    notification.save()
    return 200, notification
