import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from documents.models import Document


@pytest.mark.django_db
class TestDocumentModel:

    def test_create_document(self, user, pdf_file):
        """Тест создания документа"""
        doc = Document.objects.create(
            user=user,
            title='Test Document',
            file=pdf_file,
            file_type='.pdf',
            file_size=19,
        )
        assert doc.title == 'Test Document'
        assert doc.status == Document.Status.PENDING
        assert doc.user == user

    def test_document_str(self, document):
        """Тест строкового представления"""
        assert 'Test Document' in str(document)
        assert 'На рассмотрении' in str(document)

    def test_file_extension_validation_valid(self, user):
        """Тест валидации допустимых расширений"""
        for ext in ['.pdf', '.docx', '.xlsx', '.jpg', '.dwg']:
            file = SimpleUploadedFile(
                f'test{ext}',
                b'content',
                content_type='application/octet-stream'
            )
            doc = Document(
                user=user,
                title=f'Test {ext}',
                file=file,
                file_type=ext,
                file_size=7,
            )
            doc.full_clean()

    def test_file_extension_validation_invalid(self, user):
        """Тест валидации недопустимых расширений"""
        invalid_file = SimpleUploadedFile(
            'test.exe',
            b'file_content',
            content_type='application/octet-stream'
        )
        doc = Document(
            user=user,
            title='Bad file',
            file=invalid_file,
            file_type='.exe',
            file_size=12,
        )
        with pytest.raises(ValidationError):
            doc.full_clean()

    def test_document_status_choices(self, document):
        """Тест статусов документа"""
        assert document.status == Document.Status.PENDING

        document.status = Document.Status.APPROVED
        document.save()
        assert document.status == Document.Status.APPROVED

        document.status = Document.Status.REJECTED
        document.save()
        assert document.status == Document.Status.REJECTED

    def test_document_ordering(self, user, pdf_file):
        """Тест сортировки документов (новые сначала)"""
        doc1 = Document.objects.create(
            user=user, title='First', file=pdf_file,
            file_type='.pdf', file_size=7,
        )
        doc2 = Document.objects.create(
            user=user, title='Second', file=pdf_file,
            file_type='.pdf', file_size=7,
        )
        documents = list(Document.objects.filter(user=user))
        assert documents[0] == doc2  # Новый документ первый

    def test_document_belongs_to_user(self, user, document):
        """Тест связи документ-пользователь"""
        assert document.user == user
        assert document in user.documents.all()