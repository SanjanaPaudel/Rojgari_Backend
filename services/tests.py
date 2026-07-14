from django.test import TestCase

# Create your tests here.
# services/tests.py

from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from accounts.models import Skill

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