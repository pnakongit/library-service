from typing import Type

from rest_framework import viewsets, mixins
from rest_framework.serializers import Serializer

from borrowing.models import Borrowing
from borrowing.serializers import BorrowingSerializer, BorrowingCreateSerializer


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.all()

    def get_serializer_class(self) -> Type[Serializer]:
        if self.action == "create":
            return BorrowingCreateSerializer
        return BorrowingSerializer
