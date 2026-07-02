from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from accounts.services.auth_service import AuthService
from accounts.services.otp_service import OTPService
from accounts.serializers import SignupSerializer

from accounts.serializers import (
    VerifyOTPSerializer,
    ResendOTPSerializer,
)
from accounts.services.auth_service import AuthService


@api_view(["POST"])
@permission_classes([AllowAny])
def signup(request):

    serializer = SignupSerializer(data=request.data)

    if serializer.is_valid():

        result = AuthService.create_user_registration(
            serializer.validated_data
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    return Response(
        serializer.errors,
        status=status.HTTP_400_BAD_REQUEST,
    )


# @api_view(["POST"])
# @permission_classes([AllowAny])
# def worker_signup(request):

#     serializer = SignupSerializer(data=request.data)

#     if serializer.is_valid():

#         result = AuthService.create_worker(
#             serializer.validated_data
#         )

#         return Response(
#             result,
#             status=status.HTTP_200_OK,
#         )

#     return Response(
#         serializer.errors,
#         status=status.HTTP_400_BAD_REQUEST,
#     )


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

    result = OTPService.resend_otp(
        serializer.validated_data["phone_number"]
    )

    if result["success"]:
        return Response(
            result,
            status=status.HTTP_200_OK,
        )

    return Response(
        result,
        status=status.HTTP_400_BAD_REQUEST,
    )