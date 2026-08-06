from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.services.otp_service import OTPService
from admin_panel.serializers import (
    AdminLoginSerializer,
    CreateAdminSerializer,
)

from .services.admin_auth_service import AdminAuthService


@api_view(["POST"])
@permission_classes([AllowAny])
def admin_login(request):
    serializer = AdminLoginSerializer(data=request.data)
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
                "email": user.email,
                "role": user.role,
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


@api_view(["POST"])
@permission_classes([AllowAny])
def verify_admin_otp(request):

    phone_number = request.data.get("phone_number")
    otp = request.data.get("otp")

    result = OTPService.verify_otp(
        phone_number,
        otp,
    )

    if not result["success"]:
        return Response(result, status=400)

    user = User.objects.get(phone_number=phone_number)

    user.is_staff = True
    user.is_active = True
    user.save()

    return Response({"message": "Admin verified successfully."})
