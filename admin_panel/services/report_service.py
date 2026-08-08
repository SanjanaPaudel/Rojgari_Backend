from admin_panel.repositories.booking_repository import BookingRepository


class ReportService:
    @staticmethod
    def get_bookings_trend_24h():
        return BookingRepository.get_bookings_trend_24h()