from admin_panel.repositories.booking_repository import BookingRepository
from admin_panel.repositories.report_repository import ReportRepository


class ReportService:
    @staticmethod
    def get_bookings_trend_24h():
        return BookingRepository.get_bookings_trend_24h()

    @staticmethod
    def get_active_users_count():
        return ReportRepository.get_active_users_count()