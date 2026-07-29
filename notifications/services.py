from .models import DeviceToken


class DeviceTokenService:
    @staticmethod
    def register_device(
        user,
        token,
        device_type,
    ):

        DeviceToken.objects.update_or_create(
            token=token,
            defaults={
                "user": user,
                "device_type": device_type,
                "is_active": True,
            },
        )

        return {"message": "Device registered successfully."}
