from rest_framework import serializers


class DeviceTokenSerializer(serializers.Serializer):
    device_token = serializers.CharField()

    device_type = serializers.ChoiceField(
        choices=[
            ("android", "Android"),
            ("ios", "iOS"),
        ]
    )
