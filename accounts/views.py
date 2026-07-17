from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.serializers import (
    IdentityDocumentSerializer,
    ResendOTPSerializer,
    SelectSkillsSerializer,
    SignupSerializer,
    UpdateSkillSerializer,
    UserLoginSerializer,
    VerifyOTPSerializer,
    WorkerPhotoSerializer,
    WorkerProfileSerializer,
    WorkerStatusSerializer,
)
from accounts.permissions import IsWorker
from .services.auth_service import AuthService
from .services.dashboard_service import WorkerDashboardService
from .services.otp_service import OTPService
from .services.worker_service import WorkerService
from accounts.models import Skill
from accounts.serializers import SkillSerializer


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
    if request.user.role != "worker":
        return Response(
            {"detail": "Only workers can access this dashboard."},
            status=status.HTTP_403_FORBIDDEN,
        )

    data = WorkerDashboardService.get_dashboard(request.user)

    return Response(data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated])
def update_worker_status(request):

    if request.user.role != "worker":
        return Response(
            {"detail": "Only workers can update their status."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = WorkerStatusSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    result = WorkerService.update_online_status(
        request.user,
        serializer.validated_data["is_online"],
    )

    return Response(result)


@api_view(["POST"])
@permission_classes([AllowAny])
def user_login(request):
    serializer = UserLoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = AuthService.login(serializer.validated_data)

    refresh = RefreshToken.for_user(user)

    next_screen = ""

    if user.role == "customer":
        next_screen = "customer_dashboard"

    elif user.role == "worker":
        if user.workerprofile.has_selected_skills:
            next_screen = "worker_dashboard"
        else:
            next_screen = "select_skills"

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
            "next_screen": next_screen,
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


@api_view(["GET"])
@permission_classes([IsAuthenticated, IsWorker])
def get_skills(request):
    skills = Skill.objects.filter(is_active=True)

    serializer = SkillSerializer(
        skills,
        many=True,
    )

    return Response({"skills": serializer.data})


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWorker])
def select_skills(request):
    serializer = SelectSkillsSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    worker = request.user.workerprofile

    skill_ids = serializer.validated_data["skills"]

    skills = Skill.objects.filter(id__in=skill_ids)

    worker.skills.set(skills)

    worker.has_selected_skills = True
    worker.save()

    return Response(
        {
            "message": "Skills selected successfully.",
            "selected_skills": [skill.name for skill in skills],
        },
        status=200,
    )


@api_view(["GET", "PUT"])
@permission_classes([IsAuthenticated, IsWorker])
def worker_profile(request):

    if request.method == "GET":
        data = WorkerService.get_profile(request.user)
        return Response(data)

    serializer = WorkerProfileSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    data = WorkerService.update_profile(
        request.user,
        serializer.validated_data,
    )

    return Response(
        {
            "message": "Profile updated successfully.",
            "profile": data,
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated, IsWorker])
def upload_profile_photo(request):

    serializer = WorkerPhotoSerializer(
        data=request.data,
    )

    serializer.is_valid(raise_exception=True)

    data = WorkerService.upload_profile_photo(
        request.user,
        serializer.validated_data["profile_photo"],
    )

    return Response(
        {
            "message": data["message"],
            "profile_photo": request.build_absolute_uri(data["profile_photo"]),
        }
    )


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def upload_identity_documents(request):
    if request.user.role != "worker":
        return Response(
            {"message": "Only workers can upload identity documents."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = IdentityDocumentSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    worker = WorkerService.upload_identity_documents(
        request.user,
        serializer.validated_data,
    )

    return Response(
        {
            "message": "Documents uploaded successfully.",
            "documents": {
                "citizenship_front": (
                    request.build_absolute_uri(worker.citizenship_front.url)
                    if worker.citizenship_front
                    else None
                ),
                "citizenship_back": (
                    request.build_absolute_uri(worker.citizenship_back.url)
                    if worker.citizenship_back
                    else None
                ),
                "experience_document": (
                    request.build_absolute_uri(worker.experience_document.url)
                    if worker.experience_document
                    else None
                ),
                "is_verified": worker.is_verified,
            },
        },
        status=status.HTTP_200_OK,
    )


@api_view(["PUT"])
@permission_classes([IsAuthenticated])
def update_skills(request):

    if request.user.role != "worker":
        return Response(
            {"message": "Only workers can update skills."},
            status=status.HTTP_403_FORBIDDEN,
        )

    serializer = UpdateSkillSerializer(data=request.data)

    serializer.is_valid(raise_exception=True)

    data = WorkerService.update_skills(
        request.user,
        serializer.validated_data["skill_ids"],
    )

    return Response(
        data,
        status=status.HTTP_200_OK,
    )


# Worker side location


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, IsWorker])
def update_location(request):
    latitude = request.data.get("latitude")
    longitude = request.data.get("longitude")
    
    print(latitude,longitude),

    if latitude is None or longitude is None:
        return Response(
            {"detail": "latitude and longitude are required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    profile = request.user.workerprofile
    profile.current_latitude = latitude
    profile.current_longitude = longitude
    profile.last_location_update = timezone.now()
    profile.save()

    return Response({"detail": "Location updated."})