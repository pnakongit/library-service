from typing import Type

from rest_framework import viewsets
from rest_framework.serializers import Serializer

from book.models import Book
from book.serializers import BookSerializer, BookCreateSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action in ["list", "retrieve"]:
            return BookSerializer
        return BookCreateSerializer
