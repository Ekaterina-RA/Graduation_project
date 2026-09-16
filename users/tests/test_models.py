import pytest
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestUserModel:

    def test_create_user(self):
        """Тест создания обычного пользователя"""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="TestPass123!")
        assert user.username == "testuser"
        assert user.email == "test@example.com"
        assert user.is_active == True
        assert user.is_staff == False

    def test_create_superuser(self):
        """Тест создания суперпользователя"""
        admin = User.objects.create_superuser(username="admin", email="admin@example.com", password="AdminPass123!")
        assert admin.is_staff == True
        assert admin.is_superuser == True

    def test_user_str(self):
        """Тест строкового представления"""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="TestPass123!")
        assert str(user) == "test@example.com"

    def test_email_unique(self):
        """Тест уникальности email"""
        User.objects.create_user(username="user1", email="same@example.com", password="TestPass123!")
        with pytest.raises(Exception):
            User.objects.create_user(username="user2", email="same@example.com", password="TestPass123!")
