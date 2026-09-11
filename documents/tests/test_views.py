import pytest
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.mark.django_db
class TestDocumentAPI:

    def test_upload_document_authenticated(self, api_client, pdf_file):
        """Тест загрузки документа авторизованным пользователем"""
        data = {
            "title": "Project Drawing",
            "description": "DWG file for building project",
            "file": pdf_file,
        }
        response = api_client.post("/api/v1/documents/", data, format="multipart")
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Project Drawing"

    def test_upload_document_unauthenticated(self, api_client, pdf_file):
        """Тест: неавторизованный пользователь не может загружать"""
        api_client.force_authenticate(user=None)
        data = {"title": "Test", "file": pdf_file}
        response = api_client.post("/api/v1/documents/", data, format="multipart")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_documents(self, api_client, document):
        """Тест получения списка документов"""
        response = api_client.get("/api/v1/documents/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data["results"]) >= 1

    def test_user_sees_only_own_documents(self, api_client, user, document):
        """Тест: пользователь видит только свои документы"""
        response = api_client.get("/api/v1/documents/")
        for doc in response.data["results"]:
            assert doc["username"] == user.username

    def test_admin_can_see_all_documents(self, admin_client, document):
        """Тест: админ видит все документы"""
        response = admin_client.get("/api/v1/documents/")
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_approve_document(self, admin_client, document):
        """Тест: админ может подтвердить документ"""
        url = f"/api/v1/documents/{document.id}/review/"
        data = {"action": "approve", "comment": "Все корректно"}
        response = admin_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "approved"

    def test_admin_can_reject_document(self, admin_client, document):
        """Тест: админ может отклонить документ"""
        url = f"/api/v1/documents/{document.id}/review/"
        data = {"action": "reject", "comment": "Неверный формат"}
        response = admin_client.post(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "rejected"

    def test_filter_by_status(self, api_client, document):
        """Тест фильтрации по статусу"""
        response = api_client.get("/api/v1/documents/?status=pending")
        assert response.status_code == status.HTTP_200_OK

    def test_search_by_title(self, api_client, document):
        """Тест поиска по названию"""
        response = api_client.get("/api/v1/documents/?search=Test")
        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestUserAPI:

    def test_register_user(self, api_client):
        """Тест регистрации пользователя"""
        api_client.force_authenticate(user=None)
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "NewPass123!",
            "password_confirm": "NewPass123!",
        }
        response = api_client.post("/api/v1/users/register/", data)
        assert response.status_code == status.HTTP_201_CREATED
        assert "token" in response.data

    def test_login_user(self, api_client, user):
        """Тест логина пользователя"""
        api_client.force_authenticate(user=None)
        data = {
            "username": "testuser",
            "password": "testpass123",
        }
        response = api_client.post("/api/v1/users/login/", data)
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_get_profile(self, api_client, user):
        """Тест получения профиля"""
        response = api_client.get("/api/v1/users/profile/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == user.username
