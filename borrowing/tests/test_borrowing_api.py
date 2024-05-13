import datetime
from typing import Any

from book.tests.test_book_api import sample_book
from borrowing.models import Borrowing
from user.models import User


def sample_borrowing(*, user: User, **params: Any) -> Borrowing:
    data = {
        "expected_return_date": datetime.date.today() + datetime.timedelta(days=1),
        "book": sample_book(),
        "user": user,
    }
    data.update(params)
    return Borrowing.objects.create(**data)
