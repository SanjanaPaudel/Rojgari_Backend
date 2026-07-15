from rest_framework import serializers

from .models import Skill, WorkerProfile
from .validators import (
    validate_nepal_phone,
    validate_strong_password,
    validate_unique_email,
    validate_unique_phone,
)


class BaseSignupSerializer(serializers.Serializer):
    full_name = serializers.CharField(
        max_length=255,
    )

    phone_number = serializers.CharField(
        max_length=14,
        validators=[
            validate_nepal_phone,
            validate_unique_phone,
        ],
    )

    password = serializers.CharField(
        write_only=True,
        validators=[
            validate_strong_password,
        ],
    )

    confirm_password = serializers.CharField(
        write_only=True,
    )

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            raise serializers.ValidationError(
                {"confirm_password": "Passwords do not match."}
            )

        return attrs


class SignupSerializer(BaseSignupSerializer):
    role = serializers.ChoiceField(
        choices=[
            ("customer", "Customer"),
            ("worker", "Worker"),
        ]
    )

    email = serializers.EmailField(
        validators=[
            validate_unique_email,
        ],
    )

    profile_photo = serializers.ImageField(
        required=False,
    )


class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=14,
    )
    otp = serializers.CharField(
        max_length=6,
        min_length=6,
    )


class ResendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        validators=[
            validate_nepal_phone,
        ]
    )


# Validate the Credentials for Login
class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(
        max_length=14,
        validators=[validate_nepal_phone],
    )

    password = serializers.CharField(write_only=True)


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = [
            "id",
            "name",
            "description",
            "icon",
        ]


class SelectSkillsSerializer(serializers.Serializer):
    skills = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )


class WorkerDashboardSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name")
    phone_number = serializers.CharField(source="user.phone_number")

    primary_skill = serializers.SerializerMethodField()

    class Meta:
        model = WorkerProfile

        fields = [
            "full_name",
            "phone_number",
            "profile_photo",
            "years_of_experience",
            "average_rating",
            "completed_jobs",
            "total_reviews",
            "is_verified",
            "is_online",
            "primary_skill",
        ]

    def get_primary_skill(self, obj):
        skill = obj.skills.first()

        if skill:
            return skill.name

        return None


class WorkerStatusSerializer(serializers.Serializer):
    is_online = serializers.BooleanField()


class WorkerProfileSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source="user.full_name")
    phone_number = serializers.CharField(
        source="user.phone_number",
        read_only=True,
    )
    email = serializers.EmailField(
        source="user.email",
        required=False,
        allow_blank=True,
        allow_null=True,
    )

    class Meta:
        model = WorkerProfile
        fields = [
            "full_name",
            "phone_number",
            "email",
            "about_me",
            "service_areas",
            "profile_photo",
        ]

class WorkerPhotoSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()

class IdentityDocumentSerializer(serializers.Serializer):
    citizenship_front = serializers.ImageField(
        required=True
    )

    citizenship_back = serializers.ImageField(
        required=True
    )

    experience_document = serializers.ImageField(
        required=False,
        allow_null=True,
    )

class AddSkillSerializer(serializers.Serializer):
    skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=False,
    )