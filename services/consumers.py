import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.db import models

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

    @database_sync_to_async
    def user_owns_booking(self, user, booking_id):
        # Wrapped because the ORM is sync, but connect() is async - database_sync_to_async bridges that gap safely
        return (
            Booking.objects.fileter(id=booking_id)
            .filter(models.Q(customer__user=user) | models.Q(worker__user=user))
            .exists()
        )

    async def booking_update(self, event):
        """
        Handler for {"type": "booking.update", ...} - covers status changes, worker location pushes, and job-progress updates, all riding the same booking_<id> group.
        """

        await self.send(text_data=json.dumps(event["data"]))
