from django.conf import settings
import requests

from borrowing.models import Borrowing


def get_borrowings_notification_message(borrowing: Borrowing) -> str:
    return (
        "New borrowing:\n"
        f"id: {borrowing.id}\n"
        f"borrow_date: {borrowing.borrow_date}\n"
        f"expected_return_date: {borrowing.expected_return_date}\n"
        f"book: {borrowing.book.title}\n"
        f"user: {borrowing.user.email}\n"
    )


def send_telegram_borrowing_notification(borrowing: Borrowing) -> None:
    url = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_API_KEY}/sendMessage"
    payload = {
        "chat_id": settings.TELEGRAM_CHAT_ID,
        "text": get_borrowings_notification_message(borrowing),
    }
    response = requests.post(url, data=payload)

    if response.status_code != 200 or response.json().get("ok") is False:
        print(response.json().get("errors"))

    print("Notification sent successfully")
