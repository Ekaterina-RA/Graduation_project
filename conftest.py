import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document

User = get_user_model()


@pytest.fixture
def user(db):
    """Обычный пользователь"""
    return User.objects.create_user(username="testuser", email="test@example.com", password="testpass123")


@pytest.fixture
def admin_user(db):
    """Администратор"""
    return User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass123")


@pytest.fixture
def api_client(user):
    """API клиент для обычного пользователя"""
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    """API клиент для администратора"""
    client = APIClient()
    client.force_authenticate(user=admin_user)
    return client


@pytest.fixture
def pdf_file():
    """Тестовый PDF файл"""
    return SimpleUploadedFile("test_document.pdf", b"%PDF-1.4 test content", content_type="application/pdf")


@pytest.fixture
def document(user, pdf_file):
    """Тестовый документ"""
    return Document.objects.create(
        user=user,
        title="Test Document",
        description="Test description",
        file=pdf_file,
        file_type=".pdf",
        file_size=1024,
    )
