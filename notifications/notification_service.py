from firebase_admin import messaging

from .firebase import initialize_firebase
from .models import DeviceToken


class NotificationService:

    @staticmethod
    def initialize():
        initialize_firebase()

    @staticmethod
    def send_to_user(user, title, body, data=None):
        initialize_firebase()

        tokens = DeviceToken.objects.filter(
            user=user,
            is_active=True,
        )

        if not tokens.exists():
            return False

        for device in tokens:

            try:

                message = messaging.Message(
                    notification=messaging.Notification(
                        title=title,
                        body=body,
                    ),
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
        )