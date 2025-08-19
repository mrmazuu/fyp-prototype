from rest_framework import serializers
from django.core.exceptions import ObjectDoesNotExist
from accounts.models import User, ROLE_CHOICES


def data_serializer(data):
    if "role" in data and isinstance(data["role"], str):
        data["role"] = data["role"].upper()
    if "email" in data and isinstance(data["email"], str):
        data["email"] = data["email"].lower()
    if "name" in data and isinstance(data["name"], str):
        data["name"] = data["name"].lower()
    return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user."""

    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["user_id", "email", "name", "password", "role"]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def to_internal_value(self, data):
        data = data_serializer(data)
        return super().to_internal_value(data)

    def create(self, validated_data):
        password = validated_data.pop("password")
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=ROLE_CHOICES)

    def to_internal_value(self, data):
        data = data_serializer(data)
        return super().to_internal_value(data)

    def validate(self, data):
        email = data["email"]
        password = data["password"]
        role = data["role"]

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except ObjectDoesNotExist:
            raise serializers.ValidationError({"email": ["Invalid email"]})

        # Check password separately
        if not user.check_password(password):
            raise serializers.ValidationError({"password": ["Invalid password"]})

        # Case-insensitive role check
        if user.role.upper() != role.upper():
            raise serializers.ValidationError({"role": ["Role mismatch"]})

        data["user"] = user
        return data


class UserInfoSerializer(serializers.ModelSerializer):
    """Serializer for retrieving user information."""

    class Meta:
        model = User
        fields = ["user_id", "email", "name", "role", "created_at", "updated_at"]
