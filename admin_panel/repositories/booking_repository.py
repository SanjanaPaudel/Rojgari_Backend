from django.db.models import Q

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
