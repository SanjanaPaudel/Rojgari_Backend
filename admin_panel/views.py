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

from .serializers import DashboardSerializer
from .services.admin_auth_service import AdminAuthService
from .services.dashboard_service import DashboardService
from .services.worker_verification_service import WorkerVerificationService


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

    if not result["success"]:
        return Response(
            {result["field"]: [result["message"]]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(result, status=status.HTTP_200_OK)


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


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard(request):

    if not request.user.is_staff:
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = DashboardService.get_dashboard_data()

    serializer = DashboardSerializer(data)

    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def pending_workers(request):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=403,
        )

    data = WorkerVerificationService.get_pending_workers()

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def worker_details(request, worker_id):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    worker = WorkerVerificationService.get_worker_details(worker_id)

    if worker is None:
        return Response(
            {"detail": "Worker not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    return Response(worker)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def approve_worker(request, worker_id):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )
    note = request.data.get("note", "")
    result = WorkerVerificationService.approve_worker(
        worker_id,
        request.user,
        note,
    )

    if not result["success"]:
        if result["message"] == "Worker not found.":
            return Response(
                {"detail": result["message"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": result["message"]},
            status=status.HTTP_400_BAD_REQUEST,
        )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def reject_worker(request, worker_id):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )
    note = request.data.get("note", "")
    result = WorkerVerificationService.reject_worker(
        worker_id,
        request.user,
        note,
    )

    if not result["success"]:
        if result["message"] == "Worker not found.":
            return Response(
                {"detail": result["message"]},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {"detail": result["message"]},
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {"message": result["message"]},
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def verified_workers(request):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = WorkerVerificationService.get_verified_workers()

    return Response(data)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def all_workers(request):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = WorkerVerificationService.get_all_workers()

    return Response(
        data,
        status=status.HTTP_200_OK,
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def worker_statistics(request):

    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = WorkerVerificationService.get_worker_statistics()

    return Response(
        data,
        status=status.HTTP_200_OK,
    )

@api_view(["POST"])
@permission_classes([IsAuthenticated])
def request_resubmission(request, worker_id):
    note = request.data.get("note", "")

    result = WorkerVerificationService.request_resubmission(
        worker_id,
        request.user,
        note,
    )

    if not result["success"]:
        return Response(
            result,
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        result,
        status=status.HTTP_200_OK,
    )