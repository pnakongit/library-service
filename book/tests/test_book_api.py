import random
from typing import Any

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from faker import Faker

from book.models import Book
from book.serializers import BookSerializer

BOOK_LIST_URL = reverse("book:book-list")
BOOK_DETAIL_VIEW_NAME = "book:book-detail"


def sample_book(**params: Any) -> Book:
    fake = Faker()

    data = {
        "title": fake.sentence(nb_words=5),
        "author": fake.name(),
        "cover": random.randint(0, 1),
        "inventory": random.randint(1, 15),
        "daily_fee": 0.25,
    }
    data.update(params)
    return Book.objects.create(**data)


class UnAuthenticatedBookApiTest(APITestCase):

    def setUp(self):
        self.book = sample_book()
        self.client = APIClient()
        self.detail_url = reverse(
            BOOK_DETAIL_VIEW_NAME,
            kwargs={"pk": self.book.id},
        )

    def test_list(self) -> None:
        for _ in range(5):
            sample_book()

        response = self.client.get(BOOK_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        qs = Book.objects.all()
        serializer = BookSerializer(qs, many=True)
        self.assertEqual(response.data, serializer.data)

    def test_retrieve(self) -> None:
        response = self.client.get(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        serializer = BookSerializer(instance=self.book)
        self.assertEqual(response.data, serializer.data)

    def test_create_authenticated_required(self) -> None:
        response = self.client.post(BOOK_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_authenticated_required(self) -> None:
        payload = {
            "title": self.book.title + "updated",
            "author": self.book.title + "updated",
            "cover": self.book.cover,
            "inventory": self.book.inventory + 1,
            "daily_fee": self.book.daily_fee + 0.25,
        }
        response = self.client.put(self.detail_url, data=payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_authenticated_required(self) -> None:
        response = self.client.delete(self.detail_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
