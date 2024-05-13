from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from user.serializers import UserSerializer

USER_REGISTRATION_ENDPOINT = reverse("user:user_create")
USER_MANAGE_ENDPOINT = reverse("user:me")


class UserCreateApiTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_user_creat(self) -> None:
        payload = {
            "email": "test@test.com",
            "password": "<PASSWORD>",
        }

        response = self.client.post(USER_REGISTRATION_ENDPOINT, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user_id = response.data["email"]
        user = get_user_model().objects.get(email=user_id)

        self.assertEqual(user.email, payload["email"])
        self.assertEqual(user.check_password(payload["password"]), True)
