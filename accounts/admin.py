from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import (
    Customer,
    User,
    Worker,
    WorkerDocument,
)


class CustomerInline(admin.StackedInline):
    model = Customer
    can_delete = False
    verbose_name_plural = "Customer Profile"


class WorkerInline(admin.StackedInline):
    model = Worker
    can_delete = False
    verbose_name_plural = "Worker Profile"


class CustomUserAdmin(UserAdmin):
    inlines = (CustomerInline, WorkerInline)
    list_display = (
        "username",
        "email",
        "full_name",
        "phone_number",
        "role",
        "is_verified",
        "is_staff",
    )
    search_fields = ("username", "email", "full_name", "phone_number")
    fieldsets = UserAdmin.fieldsets + (
        (
            "Rojgari Fields",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "role",
                    "profile_photo_url",
                    "is_verified",
                )
            },
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Rojgari Fields",
            {
                "fields": (
                    "full_name",
                    "phone_number",
                    "role",
                    "profile_photo_url",
                    "is_verified",
                )
            },
        ),
    )


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("user", "address", "default_lat", "default_lng", "created_at")
    search_fields = ("user__username", "user__email", "address")


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "is_available",
        "is_approved",
        "avg_rating",
        "total_jobs",
        "created_at",
    )
    list_filter = ("is_available", "is_approved")
    search_fields = ("user__username", "user__email", "bio")


@admin.register(WorkerDocument)
class WorkerDocumentAdmin(admin.ModelAdmin):
    list_display = ("worker", "document_type", "verification_status", "submitted_at")
    list_filter = ("verification_status", "document_type")
    search_fields = ("worker__user__username", "rejection_reason")


admin.site.register(User, CustomUserAdmin)
