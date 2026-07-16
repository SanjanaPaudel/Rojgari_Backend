# Register your models here.
from django.contrib import admin

from .models import Booking, BookingMedia


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "customer", "worker", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("customer__user__full_name", "description")


@admin.register(BookingMedia)
class BookingMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "media_type")
