from django.contrib import admin

from services.models import ServiceCategory, ServiceRequest, WorkerService


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name", "description")


@admin.register(WorkerService)
class WorkerServiceAdmin(admin.ModelAdmin):
    list_display = (
        "worker",
        "category",
        "years_experience",
        "skill_level",
        "hourly_rate",
    )
    list_filter = ("skill_level", "category")
    search_fields = ("worker__user__username", "category__name")


@admin.register(ServiceRequest)
class ServiceRequestAdmin(admin.ModelAdmin):
    list_display = ("customer", "category", "status", "requested_at")
    list_filter = ("status", "category")
    search_fields = ("customer__user__username", "description")
