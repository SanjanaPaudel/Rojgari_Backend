from rest_framework import serializers
from .models import Notification

class DeviceTokenSerializer(serializers.Serializer):
    device_token = serializers.CharField()

    device_type = serializers.ChoiceField(
        choices=[
            ("android", "Android"),
            ("ios", "iOS"),
        ]
    )

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ("id", "title", "body", "notification_type", "is_read", "data", "created_at")