from django.contrib.auth import get_user_model
from rest_framework import serializers

from user.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ["email", "password", "first_name", "last_name"]

        extra_kwargs = {
            "password": {
                "write_only": True,
                "style": {"input_type": "password"},
            },
        }

    def create(self, validated_data: dict) -> User:
        password = validated_data.pop("password", None)

        user = super().create(validated_data)
        if password is not None:
            user.set_password(password)
            user.save()
        return user
