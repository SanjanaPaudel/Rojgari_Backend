from django.utils import timezone

from accounts.models import Skill, WorkerProfile
from services.models import Booking


class DashboardRepository:

    @staticmethod
    def get_worker_statistics():
        return {
            "total": WorkerProfile.objects.count(),
            "verified": WorkerProfile.objects.filter(is_verified=True).count(),
            "pending": WorkerProfile.objects.filter(is_verified=False).count(),
        }

    @staticmethod
    def get_booking_statistics():

        today = timezone.now().date()

        return {
            "today": Booking.objects.filter(created_at__date=today).count(),
            "completed_today": Booking.objects.filter(
                created_at__date=today,
                status="completed",
            ).count(),
            "working_today": Booking.objects.filter(
                created_at__date=today,
                status="working",
            ).count(),
            "total": Booking.objects.count(),
            "completed": Booking.objects.filter(
                status="completed",
            ).count(),
        }

    @staticmethod
    def get_skill_statistics():

        return {
            "total": Skill.objects.count(),
        }