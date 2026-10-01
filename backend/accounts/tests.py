from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_returns_token_and_user(self):
        response = self.client.post(
            reverse("register"),
            {"email": "Asha@Example.com", "first_name": "Asha", "last_name": "K", "password": "a-strong-pass-123"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["email"], "asha@example.com")
        self.assertFalse(response.data["user"]["is_organizer"])

    def test_register_rejects_duplicate_email(self):
        User.objects.create_user(email="asha@example.com", password="a-strong-pass-123", first_name="Asha")
        response = self.client.post(
            reverse("register"),
            {"email": "asha@example.com", "first_name": "Asha", "password": "another-pass-456"},
        )
        self.assertEqual(response.status_code, 400)

    def test_login_and_me(self):
        User.objects.create_user(email="ravi@example.com", password="a-strong-pass-123", first_name="Ravi")
        response = self.client.post(reverse("login"), {"email": "ravi@example.com", "password": "a-strong-pass-123"})
        self.assertEqual(response.status_code, 200)
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {response.data['token']}")
        me = self.client.get(reverse("me"))
        self.assertEqual(me.data["email"], "ravi@example.com")

    def test_login_with_wrong_password_fails(self):
        User.objects.create_user(email="ravi@example.com", password="a-strong-pass-123", first_name="Ravi")
        response = self.client.post(reverse("login"), {"email": "ravi@example.com", "password": "wrong"})
        self.assertEqual(response.status_code, 400)
