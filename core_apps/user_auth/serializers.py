from django.contrib.auth import get_user_model
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from rest_framework import serializers

User = get_user_model()


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        model = User
        fields = [
            "email",
            "username",
            "password",
            "first_name",
            "last_name",
            "id_no",
            "security_question",
            "security_answer",
        ]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class OTPVerifySerializer(serializers.Serializer):
    """Serializer used to document the OTP verification request body for the schema.

    Contains a single `otp` field (string / numeric) with a max length of 6.
    """

    otp = serializers.CharField(max_length=6, help_text="One-time password sent to user's email")
