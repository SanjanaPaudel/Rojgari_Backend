from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone

from accounts.models import Skill, WorkerProfile
from notifications.notification_service import NotificationService
from services.matching import distance_km
from services.models import Booking, BookingMedia, BookingOffer
from services.offers import OFFER_EXPIRY_SECONDS, backfill
from services.realtime import send_booking_update


class WorkerService:
    @staticmethod
    def update_online_status(user, is_online):
        worker = WorkerProfile.objects.get(user=user)

        worker.is_online = is_online
        worker.save()

        return {
            "message": ("You are now online." if is_online else "You are now offline."),
            "is_online": worker.is_online,
        }

    @staticmethod
    def get_profile(user):
        profile = user.workerprofile

        return {
            "full_name": user.full_name,
            "phone_number": user.phone_number,
            "email": user.email,
            "about_me": profile.about_me,
            "service_areas": profile.service_areas,
            "profile_photo": (
                profile.profile_photo.url if profile.profile_photo else None
            ),
            # Document URLs allow the frontend to distinguish:
            #   is_verified=True → verified
            #   is_verified=False + front/back present →
            #       pending (awaiting admin review)
            #   is_verified=False + front/back absent →
            #       incomplete (no docs uploaded)
            "citizenship_front": (
                profile.citizenship_front.url if profile.citizenship_front else None
            ),
            "citizenship_back": (
                profile.citizenship_back.url if profile.citizenship_back else None
            ),
            "is_verified": profile.is_verified,
        }

    @staticmethod
    def update_profile(user, data):
        profile = user.workerprofile

        user_data = data.get("user", {})

        user.full_name = user_data.get(
            "full_name",
            user.full_name,
        )

        user.email = user_data.get(
            "email",
            user.email,
        )

        profile.about_me = data.get(
            "about_me",
            profile.about_me,
        )

        profile.service_areas = data.get(
            "service_areas",
            profile.service_areas,
        )

        user.save()
        profile.save()

        return WorkerService.get_profile(user)

    @staticmethod
    def upload_profile_photo(user, photo):
        profile = user.workerprofile

        profile.profile_photo = photo

        profile.save()

        return {
            "message": "Profile photo updated successfully.",
            "profile_photo": profile.profile_photo.url,
        }

    @staticmethod
    def upload_identity_documents(user, data):
        worker = user.workerprofile

        worker.citizenship_front = data["citizenship_front"]
        worker.citizenship_back = data["citizenship_back"]

        if data.get("experience_document"):
            worker.experience_document = data["experience_document"]

        # Documents uploaded.
        # Admin verification will happen later.
        worker.is_verified = False

        worker.save()

        return worker

    @staticmethod
    def update_skills(user, skill_ids):
        worker = user.workerprofile

        skills = Skill.objects.filter(
            id__in=skill_ids,
            is_active=True,
        )

        worker.skills.set(skills)

        return {
            "message": "Skills updated successfully.",
            "skills": [skill.name for skill in worker.skills.all()],
        }

    @staticmethod
    def get_incoming_requests(user):

        worker_profile = user.workerprofile

        offers = BookingOffer.objects.filter(
            worker=worker_profile,
            status="pending",
        )

        requests = []

        for offer in offers:
            offer = WorkerService._expire_if_stale(offer)

            booking = offer.booking

            requests.append(
                {
                    "offer_id": offer.id,
                    "customer_name": booking.customer.user.full_name,
                    "service": booking.category.name,
                    "service_icon": booking.category.icon or None,
                    "description": booking.description,
                    "visit_charge": float(offer.visit_charge),
                    "address": booking.address_text,
                    "distance_km": (
                        round(
                            distance_km(
                                booking.latitude,
                                booking.longitude,
                                worker_profile.current_latitude,
                                worker_profile.current_longitude,
                            ),
                            1,
                        )
                        if worker_profile.current_latitude is not None
                        and worker_profile.current_longitude is not None
                        else None
                    ),
                    "expires_in_seconds": WorkerService._seconds_remaining(offer),
                    "created_at": offer.offered_at,
                }
            )

        return {
            "count": len(requests),
            "requests": requests,
        }

    @staticmethod
    def get_request_detail(user, offer_id):

        offer = get_object_or_404(
            BookingOffer,
            id=offer_id,
            worker=user.workerprofile,
        )

        booking = offer.booking

        photos = []

        video = None

        media = BookingMedia.objects.filter(
            booking=booking,
        )

        for item in media:
            if item.media_type == "photo":
                photos.append(item.file.url)

            elif item.media_type == "video":
                video = item.file.url

        return {
            "offer_id": offer.id,
            "customer_name": booking.customer.user.full_name,
            "service": booking.category.name,
            "service_icon": booking.category.icon or None,
            "description": booking.description,
            "visit_charge": float(offer.visit_charge),
            "address": booking.address_text,
            "latitude": booking.latitude,
            "longitude": booking.longitude,
            "distance_km": (
                round(
                    distance_km(
                        booking.latitude,
                        booking.longitude,
                        user.workerprofile.current_latitude,
                        user.workerprofile.current_longitude,
                    ),
                    1,
                )
                if user.workerprofile.current_latitude is not None
                and user.workerprofile.current_longitude is not None
                else None
            ),
            "expires_in_seconds": WorkerService._seconds_remaining(offer),
            "photos": photos,
            "video": video,
            "status": offer.status,
            "created_at": booking.created_at,
        }

    @staticmethod
    @transaction.atomic
    def accept_request(user, offer_id):

        offer = BookingOffer.objects.select_for_update().get(
            id=offer_id,
            worker=user.workerprofile,
            status="pending",
        )

        offer = WorkerService._expire_if_stale(offer)

        if offer.status != "pending":
            raise ValueError("This request has expired and is no longer available.")

        booking = Booking.objects.select_for_update().get(id=offer.booking_id)

        if booking.worker_id is not None:
            raise ValueError(
                "This booking has already been assigned to another worker."
            )

        booking.worker = user.workerprofile
        booking.status = "assigned"
        booking.save()

        offer.status = "accepted"
        offer.save()

        BookingOffer.objects.filter(
            booking=booking,
            status="pending",
        ).exclude(
            id=offer.id,
        ).update(
            status="cancelled",
        )

        def _after_commit():
            send_booking_update(
                booking.id,
                {
                    "status": booking.status,
                    "worker_name": user.full_name,
                },
            )

            try:
                NotificationService.send_to_user(
                    user=booking.customer.user,
                    title="booking_accepted",
                    body=f"{booking.worker.user.full_name} accepted your booking request.",
                    notification_type="booking_accepted",
                    data={
                        "type": "booking_accepted",
                        "booking_id": str(booking.id),
                    },
                )
            except Exception as e:
                print(f"Notification failed: {e}")

        transaction.on_commit(_after_commit)

        return {
            "message": "Request accepted successfully.",
            "booking_id": booking.id,
            "status": booking.status,
            "customer_name": booking.customer.user.full_name,
        }

    @staticmethod
    @transaction.atomic
    def reject_request(user, offer_id):

        offer = BookingOffer.objects.get(
            id=offer_id,
            worker=user.workerprofile,
            status="pending",
        )

        offer.status = "rejected"
        offer.responded_at = timezone.now()
        offer.save()

        def _after_commit():
            try:
                NotificationService.send_to_user(
                    user=offer.booking.customer.user,
                    title="booking_rejected",
                    body=f"{offer.worker.user.full_name} declined your booking request.",
                    notification_type="booking_rejected",
                    data={
                        "type": "booking_rejected",
                        "booking_id": str(offer.booking.id),
                    },
                )
            except Exception as e:
                print(f"Notification failed: {e}")

        transaction.on_commit(_after_commit)

        backfill(offer.booking)

        return {
            "message": "Request rejected successfully.",
        }

    @staticmethod
    def get_current_job(user):
        offer = (
            BookingOffer.objects.select_related(
                "booking",
                "booking__customer__user",
                "booking__category",
            )
            .filter(
                worker=user.workerprofile,
                status="accepted",
            )
            .order_by("-offered_at")
            .first()
        )

        if not offer:
            return None

        booking = offer.booking

        customer = booking.customer.user

        return {
            "booking_id": booking.id,
            "request_id": f"#REQ{booking.id:05d}",
            "category": booking.category.name,
            "customer": {
                "name": customer.full_name,
                "profile_photo": (
                    customer.customer_profile.profile_photo.url
                    if customer.customer_profile.profile_photo
                    else None
                ),
            },
            "description": booking.description,
            "address": booking.address_text,
            "latitude": booking.latitude,
            "longitude": booking.longitude,
            "requested_at": booking.created_at,
            "status": booking.status,
            "distance_km": None,
        }

    @staticmethod
    def _seconds_remaining(offer):
        age_seconds = (timezone.now() - offer.offered_at).total_seconds()
        remaining = OFFER_EXPIRY_SECONDS - age_seconds
        return max(0, int(remaining))

    @staticmethod
    @transaction.atomic
    def _expire_if_stale(offer):
        """
        If `offer` is still pending but past the 120s window, expire it
        and backfill a replacement. Returns the (possibly updated) offer.
        """
        if offer.status != "pending":
            return offer

        age_seconds = (timezone.now() - offer.offered_at).total_seconds()

        if age_seconds <= OFFER_EXPIRY_SECONDS:
            return offer

        offer.status = "expired"
        offer.responded_at = timezone.now()
        offer.save()

        backfill(offer.booking)

        return offer

    @staticmethod
    def update_location(user, data):
        worker = user.workerprofile

        worker.current_latitude = data["latitude"]

        worker.current_longitude = data["longitude"]

        worker.last_location_update = timezone.now()

        worker.save()

        current_offer = (
            BookingOffer.objects.filter(
                worker=worker,
                status="accepted",
            )
            .order_by("-offered_at")
            .first()
        )

        if current_offer:
            send_booking_update(
                current_offer.booking_id,
                {
                    "latitude": str(worker.current_latitude),
                    "longitude": str(worker.current_longitude),
                },
            )

        return {"message": "Location updated successfully."}

    @staticmethod
    def start_job(user, offer_id):
        offer = BookingOffer.objects.get(
            id=offer_id,
            worker=user.workerprofile,
            status="accepted",
        )

        booking = offer.booking

        booking.status = "working"

        booking.save()

        send_booking_update(booking.id, {"status": booking.status})

        return {
            "message": "Job started successfully.",
            "status": booking.status,
        }

    @staticmethod
    def complete_job(user, offer_id):
        offer = BookingOffer.objects.get(
            id=offer_id,
            worker=user.workerprofile,
            status="accepted",
        )

        booking = offer.booking

        if booking.status != "working":
            raise ValueError("Job has not been started yet.")

        booking.status = "completed"
        booking.save()

        worker = user.workerprofile
        worker.completed_jobs += 1
        worker.save()

        send_booking_update(
            booking.id,
            {"status": booking.status},
        )

        return {
            "message": "Job completed successfully.",
            "status": booking.status,
            "completed_jobs": worker.completed_jobs,
        }
