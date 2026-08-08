from django.core.paginator import Paginator

from admin_panel.repositories.booking_repository import BookingRepository
from admin_panel.serializers import AdminBookingListSerializer


class BookingService:
    @staticmethod
    def get_bookings_list(
        search=None,
        status_filter=None,
        category_id=None,
        date_from=None,
        date_to=None,
        page=1,
        page_size=10,
    ):
        stats = BookingRepository.get_stats()

        qs = BookingRepository.get_filtered_bookings(
            search=search,
            status_filter=status_filter,
            category_id=category_id,
            date_from=date_from,
            date_to=date_to,
        )

        paginator = Paginator(qs, page_size)
        page_obj = paginator.get_page(page)

        return {
            "stats": stats,
            "results": AdminBookingListSerializer(page_obj, many=True).data,
            "pagination": {
                "current_page": page_obj.number,
                "total_pages": paginator.num_pages,
                "total_results": paginator.count,
                "page_size": page_size,
            },
        }