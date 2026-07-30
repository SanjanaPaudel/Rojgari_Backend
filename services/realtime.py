from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def send_booking_offer(worker_user_id, data):
    """
    Push a new/backfilled offer to a specific worker's personal channel.
    """

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"worker_{worker_user_id}",
        {"type": "booking.offer", "data": data},
    )


def send_booking_update(booking_id, data):
    """
    Push a status/progress change to everyone watching this booking.
    """

    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"booking_{booking_id}", {"type": "booking.update", "data": data}
    )

def send_offer_cancelled(worker_user_id, offer_id):
    """
    Tell a specific worker's app to remove a now-dead offer from their list. 
    """
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f"worker_{worker_user_id}",
        {"type": "offer.cancelled", "data": {"event": "offer_cancelled", "offer_id": offer_id}},
    )