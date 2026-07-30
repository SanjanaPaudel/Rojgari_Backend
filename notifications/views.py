from rest_framework.decorators import (
    api_view,
    permission_classes,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import DeviceTokenSerializer,NotificationSerializer
from .services import DeviceTokenService
from .models import Notification


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register_device_token(request):

    serializer = DeviceTokenSerializer(
        data=request.data,
    )

    serializer.is_valid(
        raise_exception=True,
    )

    data = DeviceTokenService.register_device(
        user=request.user,
        token=serializer.validated_data["device_token"],
        device_type=serializer.validated_data["device_type"],
    )

    return Response(data)

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notification_list(request):
    notifications = Notification.objects.filter(
        user=request.user,
    )

    serializer = NotificationSerializer(
        notifications,
        many=True,
    )

    return Response(serializer.data)