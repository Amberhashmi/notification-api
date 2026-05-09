from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase
from rest_framework import status
from .models import Notification


class NotificationAPITests(APITestCase):

    def setUp(self):
        self.user_a = User.objects.create_user(username="userA", password="pass123")
        self.user_b = User.objects.create_user(username="userB", password="pass123")

    def test_duplicate_prevention(self):
        self.client.force_authenticate(user=self.user_a)

        payload = {
            "message": "Funds Transfer Successful",
            "notification_type": "transfer"
        }

        response1 = self.client.post("/api/notifications/create/", payload)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        response2 = self.client.post("/api/notifications/create/", payload)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)
        self.assertEqual(Notification.objects.count(), 1)

    def test_get_api_returns_only_user_notifications(self):
        Notification.objects.create(user=self.user_a, message="User A msg", notification_type="info")
        Notification.objects.create(user=self.user_b, message="User B msg", notification_type="info")

        self.client.force_authenticate(user=self.user_a)
        response = self.client.get("/api/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["message"], "User A msg")

    def test_user_b_cannot_mark_user_a_notification_read(self):
        notification = Notification.objects.create(
            user=self.user_a,
            message="Private msg",
            notification_type="info"
        )

        self.client.force_authenticate(user=self.user_b)
        response = self.client.patch(f"/api/notifications/{notification.id}/read/")

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_latest_notification_comes_first(self):
        self.client.force_authenticate(user=self.user_a)

        old = Notification.objects.create(
            user=self.user_a,
            message="Old notification",
            notification_type="info"
        )

        new = Notification.objects.create(
            user=self.user_a,
            message="New notification",
            notification_type="info"
        )

        response = self.client.get("/api/notifications/")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data[0]["message"], "New notification")