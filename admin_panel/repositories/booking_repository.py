from datetime import timedelta

from django.db.models import Count, Q
from django.db.models.functions import TruncHour
from django.utils import timezone

from services.models import Booking


class BookingRepository:
    @staticmethod
    def get_stats():
        total = Booking.objects.count()
        completed = Booking.objects.filter(status="completed").count()
        cancelled = Booking.objects.filter(status="cancelled").count()
        ongoing = Booking.objects.filter(
            status__in=["active", "assigned", "working"]
        ).count()

        def pct(count):
            return round((count / total) * 100, 1) if total else 0

        return {
            "total": total,
            "completed": completed,
            "completed_pct": pct(completed),
            "ongoing": ongoing,
            "ongoing_pct": pct(ongoing),
            "cancelled": cancelled,
            "cancelled_pct": pct(cancelled),
        }

    @staticmethod
    def get_filtered_bookings(search=None, status_filter=None, category_id=None, date_from=None, date_to=None):
        qs = Booking.objects.select_related(
            "customer__user", "worker__user", "category"
        )

        if search:
            name_match = Q(customer__user__full_name__icontains=search) | Q(
                worker__user__full_name__icontains=search
            )
            if search.isdigit():
                qs = qs.filter(Q(id=int(search)) | name_match)
            else:
                qs = qs.filter(name_match)

        if status_filter:
            qs = qs.filter(status=status_filter)

        if category_id:
            qs = qs.filter(category_id=category_id)

        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        return qs.order_by("-created_at")

@staticmethod
def get_bookings_trend_24h():
    now = timezone.now()
    start = (now - timedelta(hours=23)).replace(minute=0, second=0, microsecond=0)

    counts = (
        Booking.objects.filter(created_at__gte=start)
        .annotate(hour=TruncHour("created_at"))
        .values("hour")
        .annotate(count=Count("id"))
    )
    counts_by_hour = {row["hour"]: row["count"] for row in counts}

    return [
        {
            "hour": (start + timedelta(hours=i)).isoformat(),
            "count": counts_by_hour.get(start + timedelta(hours=i), 0),
        }
        for i in range(24)
    ]
