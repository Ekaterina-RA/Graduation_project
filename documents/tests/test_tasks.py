import pytest
from unittest.mock import patch
from django.contrib.auth import get_user_model
from documents.tasks import notify_admin_new_document, notify_user_document_reviewed

User = get_user_model()


@pytest.mark.django_db
class TestCeleryTasks:

    @patch("documents.tasks.send_mail")
    def test_notify_admin_new_document(self, mock_send_mail, document):
        """Тест уведомления администратора"""
        # Создаём администратора
        User.objects.create_superuser(username="admin", email="admin@example.com", password="adminpass123")
        result = notify_admin_new_document(document.id)
        assert "Admin notification sent" in result
        assert mock_send_mail.called

    @patch("documents.tasks.send_mail")
    def test_notify_user_document_approved(self, mock_send_mail, document):
        """Тест уведомления пользователя о подтверждении"""
        from django.utils import timezone

        document.reviewed_at = timezone.now()
        document.save()
        result = notify_user_document_reviewed(document.id, "approve")
        assert "User notification sent" in result
        assert mock_send_mail.called

    @patch("documents.tasks.send_mail")
    def test_notify_user_document_rejected(self, mock_send_mail, document):
        """Тест уведомления пользователя об отклонении"""
        from django.utils import timezone

        document.reviewed_at = timezone.now()
        document.save()
        result = notify_user_document_reviewed(document.id, "reject")
        assert "User notification sent" in result
        assert mock_send_mail.called
