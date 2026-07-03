from django.conf import settings
from twilio.rest import Client


class SMSService:
    client = Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )

    @classmethod
    def send_sms(cls, phone_number, message):

        return cls.client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=f"+977{phone_number}",
        )
