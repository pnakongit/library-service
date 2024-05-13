from datetime import datetime

from django.db import transaction
from rest_framework import serializers

from book.models import Book
from book.serializers import BookSerializer
from borrowing.helpers import send_telegram_borrowing_notification
from borrowing.models import Borrowing


class BorrowingSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field="email", read_only=True)
    book = BookSerializer(read_only=True)

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "is_returned",
            "user",
            "book",
        ]


class BorrowingCreateSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Borrowing
        fields = [
            "id",
            "book",
            "user",
            "expected_return_date",
        ]

    def validate_expected_return_date(self, value: datetime.date) -> datetime.date:
        if value <= datetime.today().date():
            raise serializers.ValidationError(
                "Expected return date must be greater than current date"
            )
        return value

    def validate_book(self, value: Book) -> Book:
        if value.inventory < 1:
            raise serializers.ValidationError(
                f"{value.title.lower()} is not available for borrowing."
            )
        return value

    def create(self, validated_data: dict) -> Borrowing:
        with transaction.atomic():
            borrowing = super().create(validated_data)
            book = borrowing.book
            book.inventory -= 1
            book.save()

            send_telegram_borrowing_notification(borrowing)

        return borrowing


class BorrowingReturnSerializer(serializers.Serializer):

    def validate(self, validated_data: dict) -> dict:

        if self.instance.actual_return_date is not None:
            raise serializers.ValidationError(
                "Borrowing was already returned. Cannot return borrowing twice"
            )
        return validated_data

    def update(self, instance, validated_data) -> Borrowing:
        with transaction.atomic():
            instance.actual_return_date = datetime.now().date()
            instance.save()
            book = instance.book
            book.inventory += 1
            book.save()
        return instance
