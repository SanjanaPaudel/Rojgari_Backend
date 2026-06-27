from django.contrib import admin

from bookings.models import Booking, Review, WorkerLocationHistory


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("request", "worker", "status", "agreed_price", "accepted_at")
    list_filter = ("status",)
    search_fields = ("request__customer__user__username", "worker__user__username")


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("booking", "reviewer", "reviewee", "rating", "created_at")
    list_filter = ("rating",)
    search_fields = ("reviewer__username", "reviewee__username", "comment")


@admin.register(WorkerLocationHistory)
class WorkerLocationHistoryAdmin(admin.ModelAdmin):
    list_display = ("worker", "lat", "lng", "recorded_at")
    search_fields = ("worker__user__username",)
