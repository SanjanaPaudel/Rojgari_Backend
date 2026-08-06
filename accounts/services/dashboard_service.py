from accounts.models import WorkerProfile
from notifications.models import Notification
from services.models import BookingOffer


class WorkerDashboardService:
    @staticmethod
    def get_dashboard(user):
        worker = (
            WorkerProfile.objects.select_related("user")
            .prefetch_related("skills")
            .get(user=user)
        )

        skills = list(
            worker.skills.values_list(
                "name",
                flat=True,
            )
        )

        incoming_request_count = BookingOffer.objects.filter(
            worker=worker,
            status="pending",
        ).count()

        unread_notifications = Notification.objects.filter(
            user=user,
            is_read=False,
        ).count()

        return {
            "worker": {
                "full_name": worker.user.full_name,
                "phone_number": worker.user.phone_number,
                "profile_photo": (
                    worker.profile_photo.url if worker.profile_photo else None
                ),
                "skills": skills,
                "years_of_experience": worker.years_of_experience,
                "verified": worker.verification_status == "verified",
                "is_online": worker.is_online,
                "stats": {
                    "jobs_done": worker.completed_jobs,
                    "skills": len(skills),
                    "reviews": worker.total_reviews,
                    "rating": float(worker.average_rating),
                },
            },
            "notifications": unread_notifications,
            "messages": 2,  # no Message model yet — left as a placeholder, see note
            "incoming_request_count": incoming_request_count,
        }
