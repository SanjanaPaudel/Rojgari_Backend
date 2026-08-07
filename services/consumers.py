import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models

from .messages import create_message
from .models import Booking


class BookingStatusConsumer(AsyncWebsocketConsumer):
    """
    One consumer instance per connected client (customer or worker)
    watching a specific booking. Joins booking_<id>, but only after
    confirming this user is actually allowed to see that booking.
    """

    async def connect(self):
        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.booking_id = self.scope["url_route"]["kwargs"]["booking_id"]

        allowed = await self.user_owns_booking(user, self.booking_id)
        if not allowed:
            await self.close(code=4003)
            return

        self.group_name = f"booking_{self.booking_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        """
        Only chat messages come in from the client -status/location updates are server -> clinet only, pushed via REST views calls into services/realtime.py, never sent back up this socker.
        """
        try:
            payload = json.loads(text_data)
        except json.JSONDecodeError:
            return

        if payload.get("type") != "chat.message":
            return

        content = (payload.get("content")or "").strip()
        if not content:
            return

        user = self.scope["user"]
        await self.save_and_broadcast_message(user, self.booking_id, content)

    @database_sync_to_async
    def save_and_broadcast_message(self, user, booking_id, content):
        # create_message() persists the Message row AND triggers the group broadcast itself (see services/messages.py), so nothing further is needed here after this call returns.

        booking = Booking.objects.get(id=booking_id)
        create_message(booking, user, content)

    @database_sync_to_async
    def user_owns_booking(self, user, booking_id):
        # Wrapped because the ORM is sync, but connect() is async - database_sync_to_async bridges that gap safely
        return (
            Booking.objects.filter(id=booking_id)
            .filter(models.Q(customer__user=user) | models.Q(worker__user=user))
            .exists()
        )

    async def booking_update(self, event):
        """
        Handler for {"type": "booking.update", ...} - covers status changes, worker location pushes, and job-progress updates, all riding the same booking_<id> group.
        """

        await self.send(text_data=json.dumps(event["data"]))

    async def chat_message(self, event):
        """
        Handler for {"type": "chat.message", ...} - forwards a persisted chat message to this client. Channels maps "chat.message" -> this method automatically (dots become underscores).
        """

        await self.send(text_data=json.dumps(event["data"]))