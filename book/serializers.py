from rest_framework import serializers

from book.models import Book


class BookSerializer(serializers.ModelSerializer):
    cover = serializers.CharField(source="get_cover_display", read_only=True)

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee_display",
        ]


class BookCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Book
        fields = [
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee",
        ]
