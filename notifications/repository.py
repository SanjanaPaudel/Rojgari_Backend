from notifications.models import Notification
from django.shortcuts import get_object_or_404

class NotificationRepository:
    @staticmethod
    def create_notification(
        *,
        user,
        title,
        body,
        notification_type,
        data=None,
    ):
        """
        Save notification into database.
        """

        return Notification.objects.create(
            user=user,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data or {},
        )
    


    @staticmethod
    def mark_as_read(notification_id, user):
        notification = get_object_or_404(
            Notification,
            id=notification_id,
            user=user,
        )

        notification.is_read = True
        notification.save()

        return notification
    