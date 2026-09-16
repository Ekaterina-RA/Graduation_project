import pytest
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestRegisterAPI:

    def test_register_success(self):
        """Тест успешной регистрации"""
        client = APIClient()
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "NewPass123!",
            "password_confirm": "NewPass123!",
        }
        response = client.post("/api/v1/users/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data
        assert User.objects.filter(username="newuser").exists()

    def test_register_passwords_mismatch(self):
        """Тест: пароли не совпадают"""
        client = APIClient()
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "NewPass123!",
            "password_confirm": "WrongPass456!",
        }
        response = client.post("/api/v1/users/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_short_password(self):
        """Тест: пароль слишком короткий"""
        client = APIClient()
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "short",
            "password_confirm": "short",
        }
        response = client.post("/api/v1/users/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_duplicate_email(self):
        """Тест: дублирование email"""
        User.objects.create_user(username="existing", email="taken@example.com", password="TestPass123!")
        client = APIClient()
        data = {
            "username": "newuser",
            "email": "taken@example.com",
            "password": "NewPass123!",
            "password_confirm": "NewPass123!",
        }
        response = client.post("/api/v1/users/register/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestLoginAPI:

    def test_login_success(self):
        """Тест успешного входа"""
        User.objects.create_user(username="testuser", email="test@example.com", password="TestPass123!")
        client = APIClient()
        data = {
            "username": "testuser",
            "password": "TestPass123!",
        }
        response = client.post("/api/v1/users/login/", data)
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_login_wrong_password(self):
        """Тест: неверный пароль"""
        User.objects.create_user(username="testuser", email="test@example.com", password="TestPass123!")
        client = APIClient()
        data = {
            "username": "testuser",
            "password": "WrongPassword!",
        }
        response = client.post("/api/v1/users/login/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_nonexistent_user(self):
        """Тест: пользователь не существует"""
        client = APIClient()
        data = {
            "username": "nobody",
            "password": "TestPass123!",
        }
        response = client.post("/api/v1/users/login/", data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestProfileAPI:

    def test_get_profile_authenticated(self):
        """Тест: авторизованный пользователь видит свой профиль"""
        user = User.objects.create_user(username="testuser", email="test@example.com", password="TestPass123!")
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get("/api/v1/users/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "testuser"
        assert response.data["email"] == "test@example.com"

    def test_get_profile_unauthenticated(self):
        """Тест: неавторизованный не видит профиль"""
        client = APIClient()
        response = client.get("/api/v1/users/profile/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
