from django.contrib.auth import get_user_model
from django.test import TestCase


class UserModelTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@user.com", password="password1234"
        )

    def test_email_field_is_user_name_field(self) -> None:

        self.assertEqual(self.user.get_username(), self.user.email)

    def test_string_representation(self) -> None:

        self.assertEqual(str(self.user), f"ID:{self.user.pk} {self.user.email}")
