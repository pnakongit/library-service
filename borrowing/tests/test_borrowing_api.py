import datetime
from typing import Any
from unittest import mock

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase, APIClient

import borrowing
from book.models import Book
from book.tests.test_book_api import sample_book
from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingCreateSerializer
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


class UnAuthenticatedBorrowingAPITest(APITestCase):

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


class AuthenticatedBorrowingAPITest(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password12345",
        )
        self.borrowing = sample_borrowing(user=self.user)
        self.detail_url = reverse(
            BORROWING_DETAIL_VIEW_NAME,
            kwargs={"pk": self.borrowing.pk},
        )
        self.return_url = reverse(
            BORROWING_RETURN_VIEW_NAME,
            kwargs={"pk": self.borrowing.pk},
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_borrowing_list(self) -> None:
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        qs = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingSerializer(qs, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_borrowing_list_filtering_by_is_active_parameter(self) -> None:
        sample_borrowing(user=self.user)
        returned_borrowing = sample_borrowing(user=self.user)
        returned_borrowing.actual_return_date = datetime.date.today()
        returned_borrowing.save()

        another_user = get_user_model().objects.create_user(
            email="another_test@test.com",
            password="password1234",
        )
        sample_borrowing(user=another_user)
        another_returned_borrowing = sample_borrowing(user=self.user)
        another_returned_borrowing.actual_return_date = datetime.date.today()
        another_returned_borrowing.save()

        test_cases = [
            (Q(actual_return_date__isnull=True, user=self.user), {"is_active": True}),
            (Q(actual_return_date__isnull=False, user=self.user), {"is_active": False}),
        ]

        for q_filter, query_params in test_cases:
            with self.subTest(q_filter=q_filter, query_params=query_params):
                queryset = Borrowing.objects.filter(q_filter)

                response = self.client.get(
                    BORROWING_LIST_URL + "?" + urlencode(query_params)
                )
                self.assertEqual(response.status_code, status.HTTP_200_OK)

                serializer = BorrowingSerializer(queryset, many=True)
                self.assertEqual(response.data, serializer.data)

    def test_borrowing_list_can_see_only_own_borrowings(self) -> None:
        another_user = get_user_model().objects.create_user(
            email="another_test@test.com",
            password="password12345",
        )
        sample_borrowing(user=self.user)
        sample_borrowing(user=self.user)
        sample_borrowing(user=another_user)
        sample_borrowing(user=another_user)

        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        qs = Borrowing.objects.filter(user=self.user)
        serializer = BorrowingSerializer(qs, many=True)

        self.assertEqual(response.data, serializer.data)

    def test_borrowing_detail(self) -> None:

        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serializer = BorrowingSerializer(self.borrowing)
        self.assertEqual(response.data, serializer.data)

    def test_borrowing_detail_can_see_only_to_own_borrowing(self) -> None:
        another_user = get_user_model().objects.create_user(
            email="another_test@test.com",
            password="password12345",
        )
        another_user_borrowing = sample_borrowing(user=another_user)

        another_user_borrowing_url = reverse(
            BORROWING_DETAIL_VIEW_NAME,
            kwargs={"pk": another_user_borrowing.pk},
        )

        response = self.client.get(another_user_borrowing_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    @mock.patch(
        f"{BorrowingCreateSerializer.__module__}.send_telegram_borrowing_notification"
    )
    def test_borrowing_create_with_authenticated_user(
        self,
        mock_send_telegram_borrowing_notification,
    ) -> None:
        payload = {
            "book": sample_book().id,
            "expected_return_date": datetime.date.today() + datetime.timedelta(days=1),
        }
        response = self.client.post(BORROWING_LIST_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_borrowing = Borrowing.objects.get(id=response.data["id"])

        self.assertEqual(created_borrowing.user, self.user)
        self.assertEqual(created_borrowing.book.id, payload["book"])
        self.assertEqual(
            created_borrowing.expected_return_date, payload["expected_return_date"]
        )

    @mock.patch(
        f"{BorrowingCreateSerializer.__module__}.send_telegram_borrowing_notification"
    )
    def test_can_not_create_with_expected_return_date_in_the_past_or_today(
        self,
        mock_send_telegram_borrowing_notification,
    ) -> None:
        incorrect_payload = {
            "book": sample_book().id,
            "expected_return_date": datetime.date.today(),
        }
        response = self.client.post(BORROWING_LIST_URL, data=incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data["expected_return_date"],
            ValidationError(
                "Expected return date must be greater than current date"
            ).detail,
        )

    @mock.patch(
        f"{BorrowingCreateSerializer.__module__}.send_telegram_borrowing_notification"
    )
    def test_can_not_create_if_book_inventory_equal_0(
        self,
        mock_send_telegram_borrowing_notification,
    ) -> None:
        book = sample_book(inventory=0)
        incorrect_payload = {
            "book": book.id,
            "expected_return_date": datetime.date.today() + datetime.timedelta(days=1),
        }
        response = self.client.post(BORROWING_LIST_URL, data=incorrect_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertEqual(
            response.data["book"],
            ValidationError(
                f"{book.title.lower()} is not available for borrowing."
            ).detail,
        )

    @mock.patch(
        f"{BorrowingCreateSerializer.__module__}.send_telegram_borrowing_notification"
    )
    def test_create_decrease_book_inventory_by_1(
        self,
        mock_send_telegram_borrowing_notification,
    ) -> None:
        book_inventory = 2
        payload = {
            "book": sample_book(inventory=book_inventory).id,
            "expected_return_date": datetime.date.today() + datetime.timedelta(days=1),
        }
        response = self.client.post(BORROWING_LIST_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        book = Book.objects.get(id=payload["book"])
        self.assertEqual(book.inventory, book_inventory - 1)

    @mock.patch(
        f"{BorrowingCreateSerializer.__module__}.send_telegram_borrowing_notification"
    )
    def test_create_sent_notification(
        self,
        mock_send_telegram_borrowing_notification,
    ) -> None:

        payload = {
            "book": sample_book().id,
            "expected_return_date": datetime.date.today() + datetime.timedelta(days=1),
        }
        response = self.client.post(BORROWING_LIST_URL, data=payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        created_borrowing = Borrowing.objects.get(id=response.data["id"])
        mock_send_telegram_borrowing_notification.assert_called_once_with(
            created_borrowing
        )

    def test_return_borrowing(self) -> None:
        borrowing = self.borrowing
        self.assertFalse(borrowing.is_returned)

        response = self.client.post(self.return_url, data={})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        borrowing.refresh_from_db()
        self.assertTrue(self.borrowing.is_returned)

    def test_return_borrowing_increase_book_inventory_by_1(self) -> None:
        borrowing = self.borrowing
        current_inventory = borrowing.book.inventory

        response = self.client.post(self.return_url, data={})
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        borrowing.book.refresh_from_db()
        self.assertEqual(borrowing.book.inventory, current_inventory + 1)

    def test_return_user_can_return_only_own_borrowing(self) -> None:
        another_user = get_user_model().objects.create_user(
            email="another_test@test.com",
            password="password1234",
        )
        another_borrowing = sample_borrowing(user=another_user)

        another_borrowing_return_url = reverse(
            BORROWING_RETURN_VIEW_NAME,
            kwargs={"pk": another_borrowing.id},
        )

        response = self.client.post(another_borrowing_return_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_return_borrowing_can_not_be_returned_twice(self) -> None:
        borrowing = self.borrowing

        response = self.client.post(self.return_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        borrowing.refresh_from_db()
        self.assertTrue(borrowing.is_returned)

        response = self.client.post(self.return_url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data["non_field_errors"],
            ValidationError(
                "Borrowing was already returned. Cannot return borrowing twice"
            ).detail,
        )
