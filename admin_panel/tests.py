from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient

from accounts.models import User


class AdminPanelAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            email="admin@test.com",
            password="Admin@123",
            full_name="Test Admin",
            phone_number="9800000000",
            role="admin",
        )

        self.admin.is_staff = True
        self.admin.is_active = True
        self.admin.save()

        self.customer = User.objects.create_user(
            email="customer@test.com",
            password="Customer@123",
            full_name="Test Customer",
            phone_number="9811111111",
            role="customer",
        )

        self.client.force_authenticate(user=self.admin)

    # ============================================================
    # ADMIN LOGIN
    # ============================================================

    @patch("admin_panel.views.AdminAuthService.login")
    def test_admin_login(self, mock_login):
        mock_login.return_value = self.admin

        response = self.client.post(
            "/api/admin/login/",
            {
                "email": "admin@test.com",
                "password": "Admin@123",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertIn("user", response.data)

    # ============================================================
    # DASHBOARD
    # ============================================================

    @patch("admin_panel.views.DashboardService.get_dashboard_data")
    def test_dashboard(self, mock_dashboard):
        mock_dashboard.return_value = {
            "workers": {
                "all": 10,
                "pending": 3,
                "verified": 5,
                "rejected": 2,
            },
            "bookings": {
                "today": 4,
                "completed_today": 2,
                "working_today": 1,
                "total": 30,
                "completed": 20,
            },
            "skills": {
                "total": 10,
            },
        }

        response = self.client.get("/api/admin/dashboard/")

        self.assertEqual(response.status_code, 200)
        self.assertIn("workers", response.data)
        self.assertIn("bookings", response.data)
        self.assertIn("skills", response.data)

    # ============================================================
    # ALL WORKERS
    # IMPORTANT:
    # This is the worker list API used by frontend.
    # Do NOT test pending/verified list APIs here.
    # ============================================================

    @patch("admin_panel.views.WorkerVerificationService.get_all_workers")
    def test_all_workers(self, mock_workers):
        mock_workers.return_value = [
            {
                "id": 23,
                "full_name": "SanjanaW",
                "phone_number": "9876543211",
                "email": "sanjana@test.com",
                "profile_photo": "/media/profile.png",
                "skills": [
                    "Plumber",
                    "Electrician",
                    "Gardener",
                ],
                "primary_skill": "Plumber",
                "years_of_experience": 3,
                "verification_status": "verified",
                "submitted_on": "2026-08-07T13:31:08Z",
                "jobs_completed": 5,
                "average_rating": 4.5,
                "total_reviews": 4,
                "is_online": True,
            }
        ]

        response = self.client.get("/api/admin/workers/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        worker = response.data[0]

        self.assertIn("id", worker)
        self.assertIn("full_name", worker)
        self.assertIn("phone_number", worker)
        self.assertIn("email", worker)
        self.assertIn("profile_photo", worker)
        self.assertIn("skills", worker)
        self.assertIn("primary_skill", worker)
        self.assertIn("years_of_experience", worker)
        self.assertIn("verification_status", worker)
        self.assertIn("submitted_on", worker)
        self.assertIn("jobs_completed", worker)
        self.assertIn("average_rating", worker)
        self.assertIn("total_reviews", worker)
        self.assertIn("is_online", worker)

        # Frontend can filter this field itself.
        self.assertEqual(worker["verification_status"], "verified")
        self.assertTrue(worker["is_online"])

    # ============================================================
    # WORKER STATISTICS
    # ============================================================

    @patch("admin_panel.views.WorkerVerificationService.get_worker_statistics")
    def test_worker_statistics(self, mock_statistics):
        mock_statistics.return_value = {
            "all": 10,
            "pending": 3,
            "verified": 5,
            "rejected": 2,
            "available_now": 4,
        }

        response = self.client.get(
            "/api/admin/workers/statistics/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["all"], 10)
        self.assertEqual(response.data["pending"], 3)
        self.assertEqual(response.data["verified"], 5)
        self.assertEqual(response.data["rejected"], 2)
        self.assertEqual(response.data["available_now"], 4)

    # ============================================================
    # WORKER DETAILS
    # ============================================================

    @patch("admin_panel.views.WorkerVerificationService.get_worker_details")
    def test_worker_details(self, mock_details):
        mock_details.return_value = {
            "id": 23,
            "full_name": "SanjanaW",
            "phone_number": "9876543211",
            "email": "sanjana@test.com",
            "verification_status": "verified",
            "years_of_experience": 3,
            "about_me": "Experienced plumber.",
            "service_areas": "Kathmandu",
            "permanent_address": "Kathmandu",
            "skills": [
                "Plumber",
                "Electrician",
            ],
            "profile_photo": "/media/profile.png",
            "citizenship_front": "/media/citizenship/front.png",
            "citizenship_back": "/media/citizenship/back.png",
            "experience_document": "/media/experience.pdf",
            "submitted_on": "2026-08-07T13:31:08Z",
            "verification_history": [],
            "is_online": True,
            "years_of_experience": 3,
            "jobs_completed": 5,
            "average_rating": 4.5,
            "total_reviews": 4,
        }

        response = self.client.get(
            "/api/admin/workers/23/"
        )

        self.assertEqual(response.status_code, 200)

        self.assertEqual(response.data["id"], 23)
        self.assertEqual(response.data["full_name"], "SanjanaW")
        self.assertIn("skills", response.data)
        self.assertIn("verification_status", response.data)
        self.assertIn("verification_history", response.data)

    @patch("admin_panel.views.WorkerVerificationService.get_worker_details")
    def test_worker_details_not_found(self, mock_details):
        mock_details.return_value = None

        response = self.client.get(
            "/api/admin/workers/9999/"
        )

        self.assertEqual(response.status_code, 404)

    # ============================================================
    # APPROVE WORKER
    # ============================================================

    @patch("admin_panel.views.WorkerVerificationService.approve_worker")
    def test_approve_worker(self, mock_approve):
        mock_approve.return_value = {
            "success": True,
            "message": "Worker verified successfully.",
        }

        response = self.client.post(
            "/api/admin/workers/23/approve/",
            {
                "note": "Documents verified successfully.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            "Worker verified successfully.",
        )

        mock_approve.assert_called_once()

    # ============================================================
    # REJECT WORKER
    # ============================================================

    @patch(
        "admin_panel.views.WorkerVerificationRepository.get_worker"
    )
    @patch(
        "admin_panel.views.WorkerVerificationService.reject_worker"
    )
    def test_reject_worker(
        self,
        mock_reject,
        mock_get_worker,
    ):
        mock_get_worker.return_value = object()

        mock_reject.return_value = {
            "success": True,
            "message": "Worker rejected successfully.",
        }

        response = self.client.post(
            "/api/admin/workers/23/reject/",
            {
                "note": "Citizenship document is unclear.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

        mock_reject.assert_called_once()

    # ============================================================
    # REQUEST RESUBMISSION
    # ============================================================

    @patch(
        "admin_panel.views.WorkerVerificationService.request_resubmission"
    )
    def test_request_resubmission(self, mock_resubmission):
        mock_resubmission.return_value = {
            "success": True,
            "message": "Resubmission requested successfully.",
        }

        response = self.client.post(
            "/api/admin/workers/23/request-resubmission/",
            {
                "note": "Please upload a clearer citizenship document.",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data["success"])

    # ============================================================
    # ADMIN PROFILE - GET
    # ============================================================

    @patch("admin_panel.views.AdminAuthService.get_profile")
    def test_get_admin_profile(self, mock_profile):
        mock_profile.return_value = {
            "id": self.admin.id,
            "full_name": "Test Admin",
            "phone_number": "9800000000",
            "email": "admin@test.com",
            "profile_photo": None,
        }

        response = self.client.get(
            "/api/admin/profile/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["full_name"], "Test Admin")
        self.assertEqual(response.data["email"], "admin@test.com")

    # ============================================================
    # ADMIN PROFILE - PATCH
    # ============================================================

    @patch("admin_panel.views.AdminAuthService.update_profile")
    def test_update_admin_profile(self, mock_update):
        mock_update.return_value = {
            "message": "Profile updated successfully.",
            "profile": {
                "id": self.admin.id,
                "full_name": "Updated Admin",
                "phone_number": "9800000000",
                "email": "admin@test.com",
                "profile_photo": None,
            },
        }

        response = self.client.patch(
            "/api/admin/profile/",
            {
                "full_name": "Updated Admin",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data["message"],
            "Profile updated successfully.",
        )

    # ============================================================
    # CATEGORY LIST
    # ============================================================

    @patch("admin_panel.views.CategoryService.get_all_categories")
    def test_categories_list(self, mock_categories):
        mock_categories.return_value = []

        response = self.client.get(
            "/api/admin/categories/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [])

    # ============================================================
    # ADMIN BOOKING LIST
    # ============================================================

    @patch("admin_panel.views.BookingService.get_bookings_list")
    def test_admin_bookings_list(self, mock_bookings):
        mock_bookings.return_value = {
            "results": [],
            "count": 0,
            "page": 1,
            "page_size": 10,
        }

        response = self.client.get(
            "/api/admin/bookings/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)

    # ============================================================
    # ACTIVE USERS
    # ============================================================

    @patch("admin_panel.views.ReportService.get_active_users_count")
    def test_active_users(self, mock_count):
        mock_count.return_value = 5

        response = self.client.get(
            "/api/admin/reports/active-users/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["active_users"], 5)

    # ============================================================
    # BOOKINGS TREND
    # ============================================================

    @patch("admin_panel.views.ReportService.get_bookings_trend_24h")
    def test_bookings_trend(self, mock_trend):
        mock_trend.return_value = [
            {"hour": "10:00", "count": 2},
            {"hour": "11:00", "count": 4},
        ]

        response = self.client.get(
            "/api/admin/reports/bookings-trend/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("bookings_trend_24h", response.data)

    # ============================================================
    # PERMISSION TEST
    # ============================================================

    def test_non_admin_cannot_access_workers(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            "/api/admin/workers/"
        )

        self.assertEqual(response.status_code, 403)

    def test_non_admin_cannot_access_dashboard(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get(
            "/api/admin/dashboard/"
        )

        self.assertEqual(response.status_code, 403)