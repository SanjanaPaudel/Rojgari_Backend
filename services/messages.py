from .models import Message
from .realtime import send_chat_message

def create_message(booking, sender, content):
    """
    Persist a chat message for a booking and broadcast it to everyone currently watching that booking's group (customer + assigned worker).
    """
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
            "sender_name": sender.full_name,
            "content": message.content,
            "created_at": message.created_at.isoformat(),
        },
    )

    return message