from datetime import timedelta

from django.utils import timezone

from accounts.models import User

ACTIVE_WINDOW_MINUTES = 5


class ReportRepository:
    @staticmethod
    def get_active_users_count():
        threshold = timezone.now() - timedelta(minutes=ACTIVE_WINDOW_MINUTES)
        return User.objects.filter(last_active_at__gte=threshold).count()