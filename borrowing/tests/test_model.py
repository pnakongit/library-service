import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase


from borrowing.tests.test_borrowing_api import sample_borrowing


class BorrowingTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password1234",
        )
        self.borrowing = sample_borrowing(user=self.user)

    def test_borrowing_string_representation(self) -> None:

        self.assertEqual(str(self.borrowing), f"ID {self.borrowing.pk}")

    def test_borrowing_is_returned_getter(self) -> None:
        self.assertIsNone(self.borrowing.actual_return_date)
        self.assertFalse(self.borrowing.is_returned)

        self.borrowing.actual_return_date = datetime.date.today()
        self.borrowing.save()

        self.assertTrue(self.borrowing.is_returned)
