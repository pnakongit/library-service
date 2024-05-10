from typing import Type

from rest_framework import viewsets
from rest_framework.serializers import Serializer

from book.models import Book
from book.permissions import IsAdminOrReadOnly
from book.serializers import BookSerializer, BookCreateSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return BookSerializer
        return BookCreateSerializer
