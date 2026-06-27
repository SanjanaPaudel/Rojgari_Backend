from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import ErrorSchema, PaymentInput, PaymentOut
from bookings.models import Booking
from notifications.models import Notification
from payments.models import Payment

router = Router()


@router.post(
    "/checkout", auth=django_auth, response={201: PaymentOut, 400: ErrorSchema}
)
def record_payment(request, data: PaymentInput):
    """
    Process and record transaction status for completed bookings.
    """
    booking = get_object_or_404(Booking, id=data.booking_id)

    if hasattr(booking, "payment"):
        return 400, {
            "message": "Payment has already been initialized/completed for this booking"
        }

    payment = Payment.objects.create(
        booking=booking,
        amount=data.amount,
        method=data.method,
        status="completed",  # Mock auto-success
        transaction_ref=data.transaction_ref,
        paid_at=timezone.now(),
    )

    # Notify Worker
    Notification.objects.create(
        user=booking.worker.user,
        title="Payment Received",
        body=f"Payment of Rs.{data.amount} has been received for booking ID {booking.id}.",
        type="payment_success",
        reference_id=payment.id,
        reference_type="Payment",
    )

    return 201, payment
