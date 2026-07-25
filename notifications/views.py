from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from rest_framework.permissions import IsAuthenticated

from rest_framework.response import Response

from .serializers import DeviceTokenSerializer
from .services import DeviceTokenService


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