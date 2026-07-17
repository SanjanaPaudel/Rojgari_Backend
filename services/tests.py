# Create your tests here.
# services/tests.py

from decimal import Decimal

from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from accounts.models import CustomerProfile, Skill, WorkerProfile

from services.matching import rank_candidates
from services.models import Booking, BookingOffer

User = get_user_model()


class CategoryListTests(APITestCase):
    def setUp(self):
        self.customer = User.objects.create_user(
            email="customer@example.com",
            password="testpass123",
            full_name="Test Customer",
            phone_number="+9779800000001",
            role="customer",
        )

        self.worker = User.objects.create_user(
            email="worker@example.com",
            password="testpass123",
            full_name="Test Worker",
            phone_number="+9779800000002",
            role="worker",
        )

        Skill.objects.create(
            name="Plumber",
            description="Test plumber",
            icon="plumbing",
            is_active=True,
            display_order=0,
        )
        Skill.objects.create(
            name="Electrician",
            description="Test electrician",
            icon="electrical",
            is_active=True,
            display_order=1,
        )

    def test_customer_can_view_categories(self):
        self.client.force_authenticate(user=self.customer)

        response = self.client.get("/api/services/categories/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["categories"]), 2)

    def test_worker_cannot_view_categories(self):
        self.client.force_authenticate(user=self.worker)

        response = self.client.get("/api/services/categories/")

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_user_cannot_view_categories(self):
        response = self.client.get("/api/services/categories/")

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class BookingCreationTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            email="bookcustomer@example.com",
            password="testpass123",
            full_name="Book Customer",
            phone_number="+9779800000021",
            role="customer",
        )

        # profiles are NOT auto-created — must create explicitly
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user
        )

        self.worker_user = User.objects.create_user(
            email="bookworker@example.com",
            password="testpass123",
            full_name="Book Worker",
            phone_number="+9779800000022",
            role="worker",
        )

        self.skill = Skill.objects.create(
            name="Plumber",
            description="Plumbing",
            icon="plumbing",
            is_active=True,
            display_order=0,
        )

        # explicit creation here too, not user.workerprofile
        self.worker_profile = WorkerProfile.objects.create(
            user=self.worker_user,
            is_online=True,
            is_verified=True,
            average_rating=Decimal("4.5"),
            completed_jobs=8,
            current_latitude=Decimal("27.7172"),
            current_longitude=Decimal("85.3240"),
            last_location_update=timezone.now(),
        )
        self.worker_profile.skills.add(self.skill)

    def test_create_booking_creates_offers_for_eligible_worker(self):
        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            "/api/services/bookings/",
            {
                "category": self.skill.id,
                "description": "Leaking pipe",
                "latitude": "27.7180",
                "longitude": "85.3245",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        booking = Booking.objects.get(id=response.data["id"])

        self.assertEqual(BookingOffer.objects.filter(booking=booking).count(), 1)
        self.assertEqual(
            BookingOffer.objects.get(booking=booking).worker, self.worker_profile
        )

    def test_create_booking_with_no_eligible_workers_still_succeeds(self):
        self.worker_profile.is_online = False
        self.worker_profile.save()

        self.client.force_authenticate(user=self.customer_user)

        response = self.client.post(
            "/api/services/bookings/",
            {
                "category": self.skill.id,
                "description": "Leaking pipe",
                "latitude": "27.7180",
                "longitude": "85.3245",
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["status"], "active")

        booking = Booking.objects.get(id=response.data["id"])
        self.assertEqual(BookingOffer.objects.filter(booking=booking).count(), 0)


class MatchingTests(APITestCase):
    def setUp(self):
        self.customer_user = User.objects.create_user(
            email="matchcustomer@example.com",
            password="testpass123",
            full_name="Match Customer",
            phone_number="+9779800000031",
            role="customer",
        )

        # explicit creation, not user.customer_profile
        self.customer_profile = CustomerProfile.objects.create(
            user=self.customer_user
        )

        self.skill = Skill.objects.create(
            name="Electrician",
            description="Electrical",
            icon="electrical",
            is_active=True,
            display_order=1,
        )

        self.booking = Booking.objects.create(
            customer=self.customer_profile,
            category=self.skill,
            description="Test",
            latitude=Decimal("27.7172"),
            longitude=Decimal("85.3240"),
            status="active",
        )

    def _make_worker(self, email, phone, lat, lon, rating, jobs, online=True):
        user = User.objects.create_user(
            email=email,
            password="testpass123",
            full_name="Worker",
            phone_number=phone,
            role="worker",
        )

        # explicit creation, not user.workerprofile
        profile = WorkerProfile.objects.create(
            user=user,
            is_online=online,
            is_verified=True,
            average_rating=Decimal(str(rating)),
            completed_jobs=jobs,
            current_latitude=Decimal(str(lat)),
            current_longitude=Decimal(str(lon)),
            last_location_update=timezone.now(),
        )
        profile.skills.add(self.skill)

        return profile

    def test_nearest_higher_rated_worker_ranks_first(self):
        near_worker = self._make_worker(
            "near@example.com", "+9779800000041", 27.7175, 85.3242, 4.8, 20
        )
        far_worker = self._make_worker(
            "far@example.com", "+9779800000042", 27.8000, 85.4000, 4.9, 20
        )

        ranked = rank_candidates(self.booking)

        self.assertEqual(ranked[0][0], near_worker)
        self.assertEqual(ranked[1][0], far_worker)

    def test_offline_worker_excluded(self):
        self._make_worker(
            "offline@example.com",
            "+9779800000043",
            27.7175,
            85.3242,
            4.8,
            20,
            online=False,
        )

        ranked = rank_candidates(self.booking)

        self.assertEqual(len(ranked), 0)

    def test_exclude_worker_ids_removes_from_candidates(self):
        worker = self._make_worker(
            "excludetest@example.com", "+9779800000044", 27.7175, 85.3242, 4.8, 20
        )

        ranked = rank_candidates(self.booking, exclude_worker_ids=[worker.id])

        self.assertEqual(len(ranked), 0)