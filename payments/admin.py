from django.contrib import admin

from payments.models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "booking",
        "amount",
        "method",
        "status",
        "transaction_ref",
        "paid_at",
    )
    list_filter = ("status", "method")
    search_fields = ("transaction_ref", "booking__request__customer__user__username")
