from admin_panel.repository import DashboardRepository


class DashboardService:
    @staticmethod
    def get_dashboard_data():

        return {
            "workers": DashboardRepository.get_worker_statistics(),
            "bookings": DashboardRepository.get_booking_statistics(),
            "skills": DashboardRepository.get_skill_statistics(),
        }
