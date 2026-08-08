# Create your tests here.
# Create your tests here.
# notifications/tests.py

from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from notifications.models import DeviceToken, Notification
from notifications.services import DeviceTokenService

User = get_user_model()


class DeviceTokenRegistrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="devicecustomer@example.com",
            password="testpass123",
            full_name="Device Customer",
            phone_number="+9779841000010",
            role="customer",
        )

    def test_register_device_creates_new_token(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(
            "/api/notifications/device-token/",
            {"device_token": "fcm-token-abc", "device_type": "android"},
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = DeviceToken.objects.get(token="fcm-token-abc")
        self.assertEqual(token.user, self.user)
        self.assertTrue(token.is_active)

    def test_registering_same_token_again_updates_it_instead_of_duplicating(self):
        DeviceTokenService.register_device(
            user=self.user, token="fcm-token-xyz", device_type="ios"
        )

        other_user = User.objects.create_user(
            email="otherdevice@example.com",
            password="testpass123",
            full_name="Other Device User",
            phone_number="+9779841000011",
            role="customer",
        )

        # Same token re-registered under a different user (e.g. device
        # changed hands / re-logged in as someone else on the same phone).
        DeviceTokenService.register_device(
            user=other_user, token="fcm-token-xyz", device_type="ios"
        )

        self.assertEqual(DeviceToken.objects.filter(token="fcm-token-xyz").count(), 1)
        token = DeviceToken.objects.get(token="fcm-token-xyz")
        self.assertEqual(token.user, other_user)

    def test_unauthenticated_user_cannot_register_device(self):
        response = self.client.post(
            "/api/notifications/device-token/",
            {"device_token": "fcm-token-anon", "device_type": "android"},
        )

        self.assertIn(
            response.status_code,
            [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN],
        )


class NotificationListTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="notifuser@example.com",
            password="testpass123",
            full_name="Notif User",
            phone_number="+9779841000012",
            role="customer",
        )

        self.other_user = User.objects.create_user(
            email="othernotifuser@example.com",
            password="testpass123",
            full_name="Other Notif User",
            phone_number="+9779841000013",
            role="customer",
        )

        Notification.objects.create(
            user=self.user,
            title="booking_accepted",
            body="Your booking was accepted.",
            notification_type="booking_accepted",
        )
        Notification.objects.create(
            user=self.user,
            title="booking_rejected",
            body="Your booking was declined.",
            notification_type="booking_rejected",
        )
        # Belongs to someone else - must never show up in self.user's list.
        Notification.objects.create(
            user=self.other_user,
            title="booking_accepted",
            body="A different user's notification.",
            notification_type="booking_accepted",
        )

    def test_notification_list_only_returns_own_notifications(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        for item in response.data:
            self.assertNotEqual(item["title"], "")

    def test_unread_count_reflects_only_unread_notifications(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get("/api/notifications/unread-count/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["unread_count"], 2)

    def test_mark_notification_read_updates_status_and_unread_count(self):
        self.client.force_authenticate(user=self.user)
        notification = Notification.objects.filter(user=self.user).first()

        response = self.client.patch(
            f"/api/notifications/{notification.id}/read/"
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)

        count_response = self.client.get("/api/notifications/unread-count/")
        self.assertEqual(count_response.data["unread_count"], 1)

    def test_cannot_mark_another_users_notification_as_read(self):
        self.client.force_authenticate(user=self.user)
        other_notification = Notification.objects.get(user=self.other_user)

        response = self.client.patch(
            f"/api/notifications/{other_notification.id}/read/"
        )

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        other_notification.refresh_from_db()
        self.assertFalse(other_notification.is_read)