from typing import Type, Any

from rest_framework import viewsets
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer, BookCreateSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def list(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Return a list of books."""
        return super().list(request, *args, **kwargs)

    def retrieve(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Retrieve a book detail by its ID."""
        return super().retrieve(request, *args, **kwargs)

    def create(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Create a new book. Available only for an admin."""
        return super().create(request, *args, **kwargs)

    def update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Update a book by its ID. Available only for an admin."""
        return super().update(request, *args, **kwargs)

    def partial_update(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Partial update a book by its ID. Available only for an admin."""
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Destroy a book by its ID. Available only for an admin."""
        return super().destroy(request, *args, **kwargs)

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return BookSerializer
        return BookCreateSerializer
