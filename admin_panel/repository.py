from django.utils import timezone

from accounts.models import Skill, WorkerProfile
from services.models import Booking


class DashboardRepository:
    @staticmethod
    def get_worker_statistics():
        return {
            "total": WorkerProfile.objects.count(),
            "verified": WorkerProfile.objects.filter(
                verification_status="verified"
            ).count(),
            "pending": WorkerProfile.objects.filter(
                verification_status="pending"
            ).count(),
            "rejected": WorkerProfile.objects.filter(
                verification_status="rejected"
            ).count(),
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


class CategoryRepository:
    @staticmethod
    def get_all_categories():
        return Skill.objects.all().order_by("display_order", "id")

    @staticmethod
    def get_category(category_id):
        try:
            return Skill.objects.get(id=category_id)
        except Skill.DoesNotExist:
            return None

    @staticmethod
    def create_category(data):
        return Skill.objects.create(**data)

    @staticmethod
    def update_category(category, data):
        for field, value in data.items():
            setattr(category, field, value)

        category.save()
        return category

    @staticmethod
    def delete_category(category):
        category.delete()
