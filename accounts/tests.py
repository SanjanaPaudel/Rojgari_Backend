# Create your tests here.
# accounts/tests.py

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import PendingRegistration, Skill
from services.models import Booking, BookingOffer

User = get_user_model()


class SignupTests(APITestCase):
    def _valid_payload(self, **overrides):
        payload = {
            "full_name": "New Customer",
            "phone_number": "9841000001",
            "password": "StrongPass1!",
            "confirm_password": "StrongPass1!",
            "role": "customer",
            "email": "newcustomer@example.com",
        }
        payload.update(overrides)
        return payload

    def test_valid_signup_creates_pending_registration_and_sends_otp(self):
        response = self.client.post(
            "/api/auth/signup/", self._valid_payload(), format="multipart"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        # Note: the phone_number validators normalize to +977-prefixed form
        # for their own duplicate checks, but that normalized value is never
        # written back onto validated_data - AuthService stores exactly what
        # was submitted. So the pending row is keyed on the raw input here.
        pending = PendingRegistration.objects.get(phone_number="9841000001")
        self.assertEqual(pending.full_name, "New Customer")
        self.assertEqual(len(pending.otp), 6)

    def test_signup_with_existing_phone_number_fails(self):
        # Matches the raw (unnormalized) format the signup payload will send,
        # since validate_unique_phone compares against the submitted string
        # as-is rather than the +977-normalized form.
        User.objects.create_user(
            email="existing@example.com",
            password="testpass123",
            full_name="Existing User",
            phone_number="9841000002",
            role="customer",
        )

        response = self.client.post(
            "/api/auth/signup/",
            self._valid_payload(phone_number="9841000002"),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_signup_with_mismatched_passwords_fails(self):
        response = self.client.post(
            "/api/auth/signup/",
            self._valid_payload(confirm_password="Different1!"),
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PendingRegistration.objects.count(), 0)


class OTPVerificationTests(APITestCase):
    def setUp(self):
        self.pending = PendingRegistration.objects.create(
            role="customer",
            full_name="Pending Customer",
            phone_number="+9779841000003",
            email="pending@example.com",
            password=make_password("StrongPass1!"),
            otp="123456",
            expires_at=timezone.now() + timedelta(minutes=3),
        )

    def test_correct_otp_creates_user_and_removes_pending_registration(self):
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"phone_number": "+9779841000003", "otp": "123456"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["success"])

        self.assertTrue(
            User.objects.filter(phone_number="+9779841000003").exists()
        )
        self.assertFalse(
            PendingRegistration.objects.filter(
                phone_number="+9779841000003"
            ).exists()
        )

    def test_incorrect_otp_increments_attempts_without_creating_user(self):
        response = self.client.post(
            "/api/auth/verify-otp/",
            {"phone_number": "+9779841000003", "otp": "000000"},
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data["success"])

        self.pending.refresh_from_db()
        self.assertEqual(self.pending.attempts, 1)
        self.assertFalse(
            User.objects.filter(phone_number="+9779841000003").exists()
        )

    def test_expired_otp_fails_and_deletes_pending_registration(self):
        self.pending.expires_at = timezone.now() - timedelta(minutes=1)
        self.pending.save()

        response = self.client.post(
            "/api/auth/verify-otp/",
            {"phone_number": "+9779841000003", "otp": "123456"},
        )

        self.assertEqual(response.status_code, status.HTTP_410_GONE)
        self.assertFalse(response.data["success"])
        self.assertFalse(
            PendingRegistration.objects.filter(
                phone_number="+9779841000003"
            ).exists()
        )

    def test_third_wrong_attempt_deletes_pending_registration(self):
        for _ in range(2):
            self.client.post(
                "/api/auth/verify-otp/",
                {"phone_number": "+9779841000003", "otp": "000000"},
            )

        response = self.client.post(
            "/api/auth/verify-otp/",
            {"phone_number": "+9779841000003", "otp": "000000"},
        )

        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertFalse(response.data["success"])
        self.assertIn("Maximum OTP attempts", response.data["message"])
        self.assertFalse(
            PendingRegistration.objects.filter(
                phone_number="+9779841000003"
            ).exists()
        )


class LoginTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="logintest@example.com",
            password="StrongPass1!",
            full_name="Login Test",
            phone_number="+9779841000004",
            role="customer",
        )

    def test_login_with_correct_credentials_returns_tokens(self):
        response = self.client.post(
            "/api/auth/login/",
            {"phone_number": "+9779841000004", "password": "StrongPass1!"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["next_screen"], "customer_dashboard")

    def test_login_with_wrong_password_fails(self):
        response = self.client.post(
            "/api/auth/login/",
            {"phone_number": "+9779841000004", "password": "WrongPass1!"},
        )

        self.assertNotEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotIn("access", response.data)


class WorkerStatusTests(APITestCase):
    def setUp(self):
        self.worker_user = User.objects.create_user(
            email="statusworker@example.com",
            password="testpass123",
            full_name="Status Worker",
            phone_number="+9779841000005",
            role="worker",
        )

        self.customer_user = User.objects.create_user(
            email="statuscustomer@example.com",
            password="testpass123",
            full_name="Status Customer",
            phone_number="+9779841000006",
            role="customer",
        )

    def test_worker_can_update_online_status(self):
        self.client.force_authenticate(user=self.worker_user)

        response = self.client.patch(
            "/api/auth/worker/status/", {"is_online": True}
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.worker_user.workerprofile.refresh_from_db()
        self.assertTrue(self.worker_user.workerprofile.is_online)

    def test_customer_cannot_update_worker_status(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.patch(
            "/api/auth/worker/status/", {"is_online": True}
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class OfferAcceptRejectTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            email="offercustomer@example.com",
            password="testpass123",
            full_name="Offer Customer",
            phone_number="+9779841000007",
            role="customer",
        )

        self.worker_user = User.objects.create_user(
            email="offerworker@example.com",
            password="testpass123",
            full_name="Offer Worker",
            phone_number="+9779841000008",
            role="worker",
        )

        self.other_worker_user = User.objects.create_user(
            email="otherworker@example.com",
            password="testpass123",
            full_name="Other Worker",
            phone_number="+9779841000009",
            role="worker",
        )

        self.skill = Skill.objects.create(
            name="Cleaner",
            description="Cleaning",
            icon="cleaning",
            is_active=True,
            display_order=0,
        )

        self.booking = Booking.objects.create(
            customer=self.customer_user.customer_profile,
            category=self.skill,
            description="Test cleaning job",
            latitude=Decimal("27.7172"),
            longitude=Decimal("85.3240"),
            status="active",
        )

        self.offer = BookingOffer.objects.create(
            booking=self.booking,
            worker=self.worker_user.workerprofile,
            score=Decimal("8.00"),
            status="pending",
        )

        self.other_offer = BookingOffer.objects.create(
            booking=self.booking,
            worker=self.other_worker_user.workerprofile,
            score=Decimal("7.00"),
            status="pending",
        )

    def test_accept_request_assigns_booking_and_cancels_other_pending_offers(self):
        self.client.force_authenticate(user=self.worker_user)

        response = self.client.post(
            f"/api/auth/worker/request/{self.offer.id}/accept/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "assigned")
        self.assertEqual(self.booking.worker, self.worker_user.workerprofile)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "accepted")

        self.other_offer.refresh_from_db()
        self.assertEqual(self.other_offer.status, "cancelled")

    def test_accept_request_fails_if_booking_already_assigned(self):
        self.booking.worker = self.other_worker_user.workerprofile
        self.booking.status = "assigned"
        self.booking.save()

        self.client.force_authenticate(user=self.worker_user)

        response = self.client.post(
            f"/api/auth/worker/request/{self.offer.id}/accept/"
        )

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)

    def test_reject_request_marks_offer_rejected_without_touching_booking(self):
        self.client.force_authenticate(user=self.worker_user)

        response = self.client.post(
            f"/api/auth/worker/request/{self.offer.id}/reject/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.offer.refresh_from_db()
        self.assertEqual(self.offer.status, "rejected")
        self.assertIsNotNone(self.offer.responded_at)

        self.booking.refresh_from_db()
        self.assertEqual(self.booking.status, "active")