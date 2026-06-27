import json

from django.test import Client, TestCase

from accounts.factories import (
    CustomerFactory,
    ServiceCategoryFactory,
    UserFactory,
    WorkerFactory,
    WorkerServiceFactory,
)
from accounts.models import (
    Customer,
    User,
    Worker,
)


class AccountAPITestCase(TestCase):
    def setUp(self):
        self.client = Client()

        # Auth URLs
        self.register_url = "/api/auth/register"
        self.login_url = "/api/auth/login"
        self.logout_url = "/api/auth/logout"
        self.me_url = "/api/auth/me"

        # Categories & Request URLs
        self.categories_url = "/api/categories"
        self.requests_url = "/api/requests"
        self.payments_url = "/api/payments/checkout"
        self.reviews_url = "/api/reviews"

    def test_customer_registration_and_login_flow(self):
        # 1. Register Customer
        reg_data = {
            "username": "customer_test",
            "email": "customer@example.com",
            "password": "Password123!",
            "full_name": "Test Customer",
            "phone_number": "+9779841234567",
            "role": "customer",
        }
        response = self.client.post(
            self.register_url,
            data=json.dumps(reg_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["username"], "customer_test")
        self.assertEqual(data["role"], "customer")

        # Verify Customer profile was created
        user = User.objects.get(username="customer_test")
        self.assertTrue(Customer.objects.filter(user=user).exists())

        # 2. Login User
        login_data = {"username": "customer_test", "password": "Password123!"}
        response = self.client.post(
            self.login_url,
            data=json.dumps(login_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        # 3. Get Me profile details
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["username"], "customer_test")

    def test_worker_registration_and_document_flow(self):
        # 1. Register Worker
        reg_data = {
            "username": "worker_test",
            "email": "worker@example.com",
            "password": "Password123!",
            "full_name": "Test Worker",
            "phone_number": "+9779841234568",
            "role": "worker",
        }
        response = self.client.post(
            self.register_url,
            data=json.dumps(reg_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        user = User.objects.get(username="worker_test")
        self.assertTrue(Worker.objects.filter(user=user).exists())

        # 2. Login Worker
        self.client.login(username="worker_test", password="Password123!")

        # 3. Submit Document
        doc_data = {
            "document_type": "citizenship",
            "file_url": "https://example.com/citizen.jpg",
        }
        response = self.client.post(
            "/api/workers/document",
            data=json.dumps(doc_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["document_type"], "citizenship")

    def test_request_and_booking_flow(self):
        # 1. Set up categories and worker offering
        category = ServiceCategoryFactory(name="Plumbing")
        worker_user = UserFactory(
            username="plumber_bob", role="worker", is_verified=True
        )
        worker = WorkerFactory(user=worker_user, is_approved=True)
        WorkerServiceFactory(worker=worker, category=category, hourly_rate=50.00)

        # Create Customer
        customer_user = UserFactory(username="alice", role="customer")
        CustomerFactory(user=customer_user)

        # 2. Login Customer to place request
        self.client.login(username="alice", password="password123")

        # Get categories list
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        # Place Request
        req_data = {
            "category_id": str(category.id),
            "description": "Bathroom sink leak repair.",
            "customer_lat": 27.7172,
            "customer_lng": 85.3240,
            "address": "Kathmandu, Nepal",
        }
        response = self.client.post(
            self.requests_url,
            data=json.dumps(req_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        request_id = response.json()["id"]

        # 3. Login Worker to accept request
        self.client.login(username="plumber_bob", password="password123")

        response = self.client.post(
            f"/api/bookings/{request_id}/accept",
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        booking_data = response.json()
        booking_id = booking_data["id"]
        self.assertEqual(booking_data["status"], "accepted")

        # 4. Worker updates status to started
        response = self.client.put(
            f"/api/bookings/{booking_id}/status",
            data=json.dumps({"status": "started"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "started")

        # 5. Worker updates status to completed
        response = self.client.put(
            f"/api/bookings/{booking_id}/status",
            data=json.dumps({"status": "completed"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "completed")

        # 6. Customer logs back in to submit payment & review
        self.client.login(username="alice", password="password123")

        # Payment
        pay_data = {
            "booking_id": booking_id,
            "amount": 100.00,
            "method": "esewa",
            "transaction_ref": "TXN_REF_12345",
        }
        response = self.client.post(
            self.payments_url,
            data=json.dumps(pay_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)

        # Review
        rev_data = {
            "booking_id": booking_id,
            "rating": 5,
            "comment": "Excellent service!",
        }
        response = self.client.post(
            self.reviews_url,
            data=json.dumps(rev_data),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["rating"], 5)

    def test_service_categories_query_caching(self):
        from django.core.cache import cache

        cache.clear()

        # 1. Cache is initially empty
        self.assertIsNone(cache.get("active_service_categories"))

        # 2. Create a category
        category = ServiceCategoryFactory(name="Plumbing")

        # 3. API request should populate the cache
        response = self.client.get(self.categories_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)

        cached_data = cache.get("active_service_categories")
        self.assertIsNotNone(cached_data)
        self.assertEqual(len(cached_data), 1)
        self.assertEqual(cached_data[0].name, "Plumbing")

        # 4. Model save() should evict the cache
        category.description = "Updated description"
        category.save()

        self.assertIsNone(cache.get("active_service_categories"))
