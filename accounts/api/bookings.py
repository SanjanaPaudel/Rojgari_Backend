from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import BookingOut, BookingStatusUpdateInput, ErrorSchema
from bookings.models import Booking
from notifications.models import Notification
from services.models import ServiceRequest, WorkerService

router = Router()


@router.post(
    "/{request_id}/accept",
    auth=django_auth,
    response={201: BookingOut, 400: ErrorSchema},
)
def accept_service_request(request, request_id: UUID):
    """
    Accept a service request and establish a booking (Worker only).
    """
    if not hasattr(request.user, "worker_profile"):
        return 400, {"message": "Only workers can accept service requests"}

    worker = request.user.worker_profile
    if not worker.is_approved:
        return 400, {"message": "Worker account must be approved to accept bookings"}

    s_request = get_object_or_404(ServiceRequest, id=request_id, status="pending")

    # Match service categories
    offered_cat = WorkerService.objects.filter(
        worker=worker, category=s_request.category
    ).first()
    if not offered_cat:
        return 400, {"message": "You do not offer services in this category"}

    # Update request state
    s_request.status = "accepted"
    s_request.save()

    booking = Booking.objects.create(
        request=s_request,
        worker=worker,
        agreed_price=offered_cat.hourly_rate
        * 2,  # Initial standard booking estimate (2 hours)
        status="accepted",
    )

    # Trigger Notification for Customer
    Notification.objects.create(
        user=s_request.customer.user,
        title="Request Accepted!",
        body=f"Worker {worker.user.full_name or worker.user.username} accepted your request.",
        type="booking_update",
        reference_id=booking.id,
        reference_type="Booking",
    )

    return 201, booking


@router.put(
    "/{booking_id}/status",
    auth=django_auth,
    response={200: BookingOut, 400: ErrorSchema},
)
def update_booking_status(request, booking_id: UUID, data: BookingStatusUpdateInput):
    """
    Modify execution status of active booking ('started', 'completed', 'cancelled').
    """
    booking = get_object_or_404(Booking, id=booking_id)

    # Authorization Check
    is_worker = (
        hasattr(request.user, "worker_profile")
        and booking.worker == request.user.worker_profile
    )
    is_customer = (
        hasattr(request.user, "customer_profile")
        and booking.request.customer == request.user.customer_profile
    )

    if not (is_worker or is_customer):
        return 400, {"message": "Unauthorized to update this booking"}

    if data.status == "started":
        if not is_worker:
            return 400, {"message": "Only the worker can mark a booking as started"}
        booking.status = "started"
        booking.started_at = timezone.now()

    elif data.status == "completed":
        if not is_worker:
            return 400, {"message": "Only the worker can mark a booking as completed"}
        booking.status = "completed"
        booking.completed_at = timezone.now()
        # Mark parent request completed
        booking.request.status = "completed"
        booking.request.save()

        # Notify Customer
        Notification.objects.create(
            user=booking.request.customer.user,
            title="Booking Completed",
            body="Your booking is marked completed. Please leave a review and complete payment.",
            type="booking_update",
            reference_id=booking.id,
            reference_type="Booking",
        )

    elif data.status == "cancelled":
        booking.status = "cancelled"
        booking.cancelled_at = timezone.now()
        booking.cancellation_reason = data.cancellation_reason
        # Revert request back to pending
        booking.request.status = "pending"
        booking.request.save()

        # Notify other party
        recipient = booking.request.customer.user if is_worker else booking.worker.user
        Notification.objects.create(
            user=recipient,
            title="Booking Cancelled",
            body=f"Booking was cancelled. Reason: {data.cancellation_reason}",
            type="booking_update",
            reference_id=booking.id,
            reference_type="Booking",
        )
    else:
        return 400, {"message": "Invalid status value"}

    booking.save()
    return 200, booking
