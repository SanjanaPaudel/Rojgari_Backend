from notifications.models import Notification


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