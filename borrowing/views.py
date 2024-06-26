from typing import Type, Any

from django.db.models import QuerySet
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from borrowing.filters import IsBorrowingOwnerOrIsAdminFilterBackend, BorrowingFilter
from borrowing.models import Borrowing
from borrowing.serializers import (
    BorrowingSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()
    permission_classes = [IsAuthenticated]
    filter_backends = [
        IsBorrowingOwnerOrIsAdminFilterBackend,
        DjangoFilterBackend,
    ]
    filterset_class = BorrowingFilter

    def get_queryset(self) -> QuerySet:
        qs = super().get_queryset()
        if self.action == "list":
            return qs.select_related("book", "user")
        return qs

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a list of own borrowings for an authenticated user.
        Return a list of all borrowings for an admin user."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Returns a single borrowing by ID. Authenticated user have access to own borrowings.
        Admin user have access to all borrowings."""
        return super().retrieve(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new borrowing."""
        return super().create(request, *args, **kwargs)

    @action(
        methods=["post"],
        detail=True,
        url_path="return",
        url_name="return",
        serializer_class=BorrowingReturnSerializer,
    )
    def return_borrowing(self, request: Request, pk: int = None) -> Response:
        """Sets actual return date of borrowing to the current date.
        Returns an error if borrowing is already returned."""
        borrowing_obj = self.get_object()
        serializer = self.get_serializer(borrowing_obj, data={})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
