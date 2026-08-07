from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import User
from accounts.services.otp_service import OTPService
from admin_panel.serializers import (
    AdminChangePasswordSerializer,
    AdminLoginSerializer,
    AdminProfilePhotoSerializer,
    AdminProfileSerializer,
    CreateAdminSerializer,
    DashboardSerializer,
)

from .repositories.worker_verification_repository import (
    WorkerVerificationRepository,
)
from .serializers import CategorySerializer
from .services.admin_auth_service import AdminAuthService
from .services.category_service import CategoryService
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


@api_view(["GET", "PATCH"])
@permission_classes([IsAuthenticated])
def admin_profile(request):
    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        data = AdminAuthService.get_profile(request.user)

        serializer = AdminProfileSerializer(data)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    serializer = AdminProfileSerializer(
        data=request.data,
    )

    serializer.is_valid(raise_exception=True)

    data = AdminAuthService.update_profile(
        request.user,
        serializer.validated_data,
    )

    return Response(
        data,
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def admin_profile_photo(request):
    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AdminProfilePhotoSerializer(
        data=request.data,
    )

    serializer.is_valid(raise_exception=True)

    data = AdminAuthService.update_profile_photo(
        request.user,
        serializer.validated_data["profile_photo"],
    )

    data["profile_photo"] = request.build_absolute_uri(data["profile_photo"])

    return Response(
        data,
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
def approve_worker(request, worker_id):
    result = WorkerVerificationService.approve_worker(
        worker_id,
        request.user,
        request.data.get("note", ""),
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


@api_view(["POST"])
def reject_worker(request, worker_id):
    worker = WorkerVerificationRepository.get_worker(worker_id)

    result = WorkerVerificationService.reject_worker(
        worker,
        request.user,
        request.data.get("note", ""),
    )

    return Response(result)


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
def request_resubmission(request, worker_id):
    result = WorkerVerificationService.request_resubmission(
        worker_id,
        request.user,
        request.data.get("note", ""),
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


@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def categories(request):
    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    if request.method == "GET":
        categories = CategoryService.get_all_categories()

        serializer = CategorySerializer(
            categories,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    serializer = CategorySerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    category = CategoryService.create_category(serializer.validated_data)

    response_serializer = CategorySerializer(category)

    return Response(
        response_serializer.data,
        status=status.HTTP_201_CREATED,
    )


@api_view(["GET", "PUT", "PATCH", "DELETE"])
@permission_classes([IsAuthenticated])
def category_detail(request, category_id):
    if request.user.role != "admin":
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    category = CategoryService.get_category(category_id)

    if category is None:
        return Response(
            {"detail": "Category not found."},
            status=status.HTTP_404_NOT_FOUND,
        )

    if request.method == "GET":
        serializer = CategorySerializer(category)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    if request.method in ["PUT", "PATCH"]:
        serializer = CategorySerializer(
            category,
            data=request.data,
            partial=request.method == "PATCH",
        )

        serializer.is_valid(raise_exception=True)

        category = CategoryService.update_category(
            category,
            serializer.validated_data,
        )

        response_serializer = CategorySerializer(category)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )

    CategoryService.delete_category(category)

    return Response(
        {"message": "Category deleted successfully."},
        status=status.HTTP_200_OK,
    )


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def change_admin_password(request):
    if not request.user.is_staff:
        return Response(
            {"detail": "Permission denied."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = AdminChangePasswordSerializer(
        data=request.data,
    )

    serializer.is_valid(raise_exception=True)

    result = AdminAuthService.change_password(
        request.user,
        serializer.validated_data,
    )

    if not result["success"]:
        return Response(
            {
                result["field"]: [result["message"]],
            },
            status=status.HTTP_400_BAD_REQUEST,
        )

    return Response(
        {
            "message": result["message"],
        },
        status=status.HTTP_200_OK,
    )
