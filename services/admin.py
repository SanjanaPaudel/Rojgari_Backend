# Register your models here.
from django.contrib import admin

from .models import Booking, BookingMedia, BookingOffer


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "category", "customer", "worker", "status", "created_at")
    list_filter = ("status", "category")
    search_fields = ("customer__user__full_name", "description")


@admin.register(BookingMedia)
class BookingMediaAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "media_type")


@admin.register(BookingOffer)
class BookingOfferAdmin(admin.ModelAdmin):
    list_display = ("id", "booking", "worker", "score", "status", "offered_at")
    list_filter = ("status",)
