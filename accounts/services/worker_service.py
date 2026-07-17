from django.db import transaction
from django.shortcuts import get_object_or_404

from accounts.models import Skill, WorkerProfile
from services.models import BookingMedia, BookingOffer


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
            #   is_verified=True                          → verified
            #   is_verified=False + front/back present    → pending (awaiting admin review)
            #   is_verified=False + front/back absent     → incomplete (no docs uploaded)
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
            booking = offer.booking

            requests.append(
                {
                    "offer_id": offer.id,
                    "customer_name": booking.customer.user.full_name,
                    "service": booking.category.name,
                    "service_icon": (
                        booking.category.icon.url if booking.category.icon else None
                    ),
                    "description": booking.description,
                    "address": booking.address_text,
                    "distance_km": 0,
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
            "service_icon": (
                booking.category.icon.url if booking.category.icon else None
            ),
            "description": booking.description,
            "address": booking.address_text,
            "latitude": booking.latitude,
            "longitude": booking.longitude,
            "distance_km": 0,
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

        booking = offer.booking

        booking.worker = user.workerprofile
        booking.status = "scheduled"
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

        return {
            "message": "Request accepted successfully.",
            "booking_id": booking.id,
            "status": booking.status,
        }
