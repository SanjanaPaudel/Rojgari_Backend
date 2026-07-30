import json

from channels.generic.websocket import AsyncWebsocketConsumer


class WorkerOfferConsumer(AsyncWebsocketConsumer):
    """
    One consumer instance per connected worker.
    Joins a personal group keyed by user.id so create_booking()
    can push offers straight to this specific worker, without knowing or caring whether they're currently connected/online.
    """

    async def connect(self):
        user = self.scope["user"]

        # AnonymousUser has is_authenticated=False; reject anyone who didn't come through valid JWT auth middleware

        if not user.is_authenticated:
            await self.close(code=4001)
            return

        self.group_name = f"worker_{user.id}"

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # group_name only exists if connect() got far enough to set it
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    # No receive() override - this consumer is push-only.
    # Worker actions (accept/reject) go through REST, not htis socket.

    async def booking_offer(self, event):
        """
        Handler for {"type": "booking.offer", ...} messages sent via group_send() Channel maps "booking.offer" -> this method automatically (dots become underscores)
        """
        await self.send(text_data=json.dumps(event["data"]))

    async def offer_cancelled(self, event):
        await self.send(text_data=json.dumps(event["data"]))
