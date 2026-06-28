from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.serializers import (
    CustomerSignupSerializer,
    WorkerSignupSerializer,
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
