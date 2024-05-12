from django.db.models import QuerySet
from rest_framework import filters


class IsBorrowingOwnerOrIsAdminFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view) -> QuerySet:
        if request.user.is_staff:
            return queryset
        return queryset.filter(user=request.user)
