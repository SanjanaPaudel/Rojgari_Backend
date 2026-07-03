from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    ResendOTPSerializer,
    SignupSerializer,
    VerifyOTPSerializer,
    UserLoginSerializer,
)
from accounts.services.auth_service import AuthService
from accounts.services.otp_service import OTPService


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):

    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():
        result = AuthService.create_user_registration(serializer.validated_data)

        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )

@api_view(["POST"])
@permission_classes([AllowAny])
def verify_otp(request):

    serializer = VerifyOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = OTPService.verify_otp(
        serializer.validated_data["phone_number"],
        serializer.validated_data["otp"],
    )

    if result["success"]:
        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    message = result["message"]

    if message == "Registration not found.":
        return Response(
            result,
            status=status.HTTP_404_NOT_FOUND,
        )

    elif message == "OTP has expired.":
        return Response(
            result,
            status=status.HTTP_410_GONE,
        )

    elif message == "Maximum OTP attempts exceeded.":
        return Response(
            result,
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    return Response(
        result,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["POST"])
@permission_classes([AllowAny])
def resend_otp(request):

    serializer = ResendOTPSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST,
        )

    result = OTPService.resend_otp(serializer.validated_data["phone_number"])

    if result["success"]:
        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    return Response(
        result,
        status=status.HTTP_400_BAD_REQUEST,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def worker_dashboard(request):

    user = request.user

    if user.role != "worker":
        return Response(
            {
                "success": False,
                "message": "Only workers can access this dashboard."
            },
            status=403,
        )

    profile = user.workerprofile

    return Response({
        "success": True,

        "worker": {

            "id": user.id,

            "full_name": user.full_name,

            "phone_number": user.phone_number,

            "email": user.email,

            "role": user.role,

            "profile_photo": (
                request.build_absolute_uri(profile.profile_photo.url)
                if profile.profile_photo
                else None
            ),

            "is_verified": profile.is_verified,

            "is_online": profile.is_online,

            "years_of_experience": profile.years_of_experience,

            "completed_jobs": profile.completed_jobs,

            "average_rating": float(profile.average_rating),

            "total_reviews": profile.total_reviews,
        }
    })
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
