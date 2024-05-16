from django.db.models import QuerySet
from rest_framework import filters
from django_filters import rest_framework as django_filters

from borrowing.models import Borrowing


class IsBorrowingOwnerOrIsAdminFilterBackend(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view) -> QuerySet:
        if request.user.is_staff:
            return queryset
        return queryset.filter(user=request.user)


class BorrowingFilter(django_filters.FilterSet):
    user_id = django_filters.NumberFilter(help_text="filtering by borrowing user")
    is_active = django_filters.BooleanFilter(
        field_name="actual_return_date",
        lookup_expr="isnull",
        help_text="filtering by borrowing status",
    )
