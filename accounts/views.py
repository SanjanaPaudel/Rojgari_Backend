from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    CustomerSignupSerializer,
    WorkerSignupSerializer,
    UserLoginSerializer,
)
from accounts.services.auth_service import AuthService


@api_view(["POST"])
@permission_classes([AllowAny])
def customer_signup(request):

    serializer = CustomerSignupSerializer(data=request.data)

    if serializer.is_valid():
        user = AuthService.create_customer(serializer.validated_data)

        return Response(
            {
                "message": "Customer account created successfully.",
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def worker_signup(request):

    serializer = WorkerSignupSerializer(data=request.data)

    if serializer.is_valid():
        user = AuthService.create_worker(serializer.validated_data)

        return Response(
            {
                "message": "Worker account created successfully.",
                "user": {
                    "id": user.id,
                    "full_name": user.full_name,
                    "phone_number": user.phone_number,
                    "email": user.email,
                    "role": user.role,
                },
            },
            status=status.HTTP_201_CREATED,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = AuthService.login(serializer.validated_data)

    refresh = RefreshToken.for_user(user)

    return Response(
        {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "full_name": user.full_name,
                "phone_number": user.phone_number,
                "role": user.role,
            },
        },
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def user_refresh(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {"detail": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        refresh = RefreshToken(refresh_token)
        new_access_token = str(refresh.access_token)
    except Exception:
        return Response(
            {"detail": "Invalid or expired refresh token."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    return Response({"access": new_access_token}, status=status.HTTP_200_OK)



@api_view(["POST"])
@permission_classes([AllowAny])
def user_logout(request):
    refresh_token = request.data.get("refresh")

    if not refresh_token:
        return Response(
            {"detail": "Refresh token is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        token = RefreshToken(refresh_token)
        token.blacklist()
    except Exception:
        return Response(
            {"detail": "Invalid or already blacklisted token."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"detail": "Successfully logged out."},
        status=status.HTTP_205_RESET_CONTENT,
    )