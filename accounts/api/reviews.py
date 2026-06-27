from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.security import django_auth

from accounts.api.schemas import ErrorSchema, ReviewInput, ReviewOut
from bookings.models import Booking, Review

router = Router()


@router.post("", auth=django_auth, response={201: ReviewOut, 400: ErrorSchema})
def submit_review(request, data: ReviewInput):
    """
    Publish a review rating (1-5) and feedback comment for a booking.
    """
    booking = get_object_or_404(Booking, id=data.booking_id)

    if booking.status != "completed":
        return 400, {"message": "Reviews can only be submitted for completed bookings"}

    # Determine Reviewer and Reviewee
    if (
        hasattr(request.user, "customer_profile")
        and booking.request.customer == request.user.customer_profile
    ):
        reviewer = request.user
        reviewee = booking.worker.user
    elif (
        hasattr(request.user, "worker_profile")
        and booking.worker == request.user.worker_profile
    ):
        reviewer = request.user
        reviewee = booking.request.customer.user
    else:
        return 400, {"message": "You are not a participant of this booking"}

    # Check for duplicate review by same reviewer on same booking
    if Review.objects.filter(booking=booking, reviewer=reviewer).exists():
        return 400, {"message": "You have already reviewed this booking"}

    if data.rating < 1 or data.rating > 5:
        return 400, {"message": "Rating must be between 1 and 5"}

    review = Review.objects.create(
        booking=booking,
        reviewer=reviewer,
        reviewee=reviewee,
        rating=data.rating,
        comment=data.comment,
    )

    # Recalculate Average Rating for Worker (if reviewee is a Worker)
    if hasattr(reviewee, "worker_profile"):
        worker = reviewee.worker_profile
        all_worker_reviews = Review.objects.filter(reviewee=reviewee)
        total_rating = sum(r.rating for r in all_worker_reviews)
        count = all_worker_reviews.count()
        worker.avg_rating = round(total_rating / count, 2)
        worker.total_jobs = count
        worker.save()

    return 201, review
