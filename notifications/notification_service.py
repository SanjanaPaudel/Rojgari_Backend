from firebase_admin import messaging

from .firebase import initialize_firebase
from .models import DeviceToken
from .repository import NotificationRepository


class NotificationService:
    @staticmethod
    def initialize():
        initialize_firebase()

    @staticmethod
    def send_to_user(user, title, body, notification_type, data=None):
        initialize_firebase()

        NotificationRepository.create_notification(
            user=user,
            title=title,
            body=body,
            notification_type=notification_type,
            data=data,
        )

        tokens = DeviceToken.objects.filter(user=user, is_active=True)

        if not tokens.exists():
            return False

        for device in tokens:
            try:
                message = messaging.Message(
                    notification=messaging.Notification(title=title, body=body),
                    token=device.token,
                    data=data or {},
                )
                messaging.send(message)
            except Exception:
                device.is_active = False
                device.save()

        return True

    @staticmethod
    def send_test_notification(user):
        return NotificationService.send_to_user(
            user=user,
            title="Rojgari",
            body="Notification system is working!",
            notification_type="booking_accepted",
        )
