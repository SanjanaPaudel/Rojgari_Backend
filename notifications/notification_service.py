from .firebase import initialize_firebase


class NotificationService:

    @staticmethod
    def initialize():
        initialize_firebase()