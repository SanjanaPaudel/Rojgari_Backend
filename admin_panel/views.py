from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import UserLoginSerializer
from accounts.services.auth_service import AuthService
from admin_panel.serializers import CreateAdminSerializer
from .services.admin_auth_service import AdminAuthService
from rest_framework.permissions import IsAuthenticated


@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = AdminAuthService.login(serializer.validated_data)

    if not user.is_staff:
        return Response(
            {"detail": "You are not authorized to access the admin panel."},
            status=status.HTTP_403_FORBIDDEN,
        )

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
            },
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_admin(request):

    if not request.user.is_staff:
        return Response(
            {"detail": "Permission denied."},
            status=403,
        )

    serializer = CreateAdminSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    result = AdminAuthService.create_admin(serializer.validated_data)

    return Response(result)