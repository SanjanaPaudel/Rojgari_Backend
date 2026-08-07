from notifications.notification_service import NotificationService

from .models import Message
from .realtime import send_chat_message


def create_message(booking, sender, content):
    """
    Persist a chat message for a booking and broadcast it to everyone
    currently watching that booking's group (customer + assigned worker).
    """
    content = content.strip()[:2000]

    message = Message.objects.create(
        booking=booking,
        sender=sender,
        content=content,
    )

    send_chat_message(
        booking.id,
        {
            "event": "chat_message",
            "id": message.id,
            "booking_id": booking.id,
            "sender_id": sender.id,
            "sender_name": sender.full_name,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        },
    )

    if sender == booking.customer.user:
        recipient = booking.worker.user if booking.worker else None
    else:
        recipient = booking.customer.user

    if recipient:
        try:
            NotificationService.send_to_user(
                user=recipient,
                title=sender.full_name,
                body=content[:100],
                notification_type="chat_message",
                data={
                    "type": "chat_message",
                    "booking_id": str(booking.id),
                },
            )
        except Exception as e:
            print(f"Chat notification failed: {e}")

    return message