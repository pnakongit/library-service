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


class UnAuthenticatedUserManageApiTest(APITestCase):

    def setUp(self):
        self.client = APIClient()

    def test_get_method_authenticate_required(self) -> None:
        self.client.logout()

        response = self.client.get(USER_MANAGE_ENDPOINT)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_method_authenticate_required(self) -> None:
        self.client.logout()

        response = self.client.put(USER_MANAGE_ENDPOINT)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_patch_method_authenticate_required(self) -> None:
        self.client.logout()

        response = self.client.patch(USER_MANAGE_ENDPOINT)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserManageApiTest(APITestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_user(self) -> None:

        response = self.client.get(USER_MANAGE_ENDPOINT)

        serializer = UserSerializer(instance=self.user)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_put_user(self) -> None:
        user = self.user
        payload = {
            "email": "new_test@test.com",
            "password": "new_password1234",
        }

        response = self.client.put(USER_MANAGE_ENDPOINT, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertEqual(user.email, payload["email"])
        self.assertTrue(user.check_password(payload["password"]))

    def test_patch_user(self) -> None:
        user = self.user
        payload = {
            "email": "new_test@test.com",
        }

        response = self.client.patch(USER_MANAGE_ENDPOINT, data=payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user.refresh_from_db()
        self.assertEqual(user.email, payload["email"])
