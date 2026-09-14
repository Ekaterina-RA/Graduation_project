from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["email", "username", "password", "password_confirm", "first_name", "last_name", "organization"]

    def validate(self, data):
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError({"password": "Пароли не совпадают"})
        return data

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "username", "first_name", "last_name", "organization", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class LoginSerializer(serializers.Serializer):
    """Сериализатор для входа — принимает username ИЛИ email"""

    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        if not data.get("username") and not data.get("email"):
            raise serializers.ValidationError("Укажите username или email")
        if not data.get("password"):
            raise serializers.ValidationError("Укажите пароль")
        return data
