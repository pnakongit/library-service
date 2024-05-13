import datetime
from typing import Any

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from book.tests.test_book_api import sample_book
from borrowing.models import Borrowing
from user.models import User

BORROWING_LIST_URL = reverse("borrowing:borrowing-list")
BORROWING_DETAIL_VIEW_NAME = "borrowing:borrowing-detail"
BORROWING_RETURN_VIEW_NAME = "borrowing:borrowing-return"


def sample_borrowing(*, user: User, **params: Any) -> Borrowing:
    data = {
        "expected_return_date": datetime.date.today() + datetime.timedelta(days=1),
        "book": sample_book(),
        "user": user,
    }
    data.update(params)
    return Borrowing.objects.create(**data)


class UnAuthenticatedBorrowingAPITestCase(APITestCase):

    def setUp(self):
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password12345",
        )
        borrowing = sample_borrowing(user=user)
        self.detail_url = reverse(
            BORROWING_DETAIL_VIEW_NAME,
            kwargs={"pk": borrowing.pk},
        )
        self.return_url = reverse(
            BORROWING_RETURN_VIEW_NAME,
            kwargs={"pk": borrowing.pk},
        )
        self.client = APIClient()

    def test_borrowing_list_authenticated_required(self) -> None:

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_detail_authenticated_required(self) -> None:

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_create_authenticated_required(self) -> None:
        response = self.client.post(BORROWING_LIST_URL, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_borrowing_return_authenticated_required(self) -> None:
        response = self.client.post(self.return_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
