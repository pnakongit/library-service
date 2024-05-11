from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CheckConstraint, Q, F

from book.models import Book


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name="borrowings")
    user = models.ForeignKey(
        get_user_model(), on_delete=models.CASCADE, related_name="borrowings"
    )

    class Meta:
        ordering = ["-borrow_date"]

        constraints = [
            CheckConstraint(
                check=Q(expected_return_date__gt=F("borrow_date")),
                name="expected_return_date_grates_than_borrow_date",
            ),
            CheckConstraint(
                check=Q(actual_return_date__gt=F("borrow_date")),
                name="actual_return_date_grates_than_borrow_date",
            ),
        ]

    def __str__(self) -> str:
        return f"ID {self.pk}"

    @property
    def is_returned(self) -> bool:
        return bool(self.actual_return_date)
