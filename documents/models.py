import os
from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError


def validate_file_extension(value):
    """Валидация расширения файла"""
    allowed_extensions = [".dwg", ".pdf", ".docx", ".xlsx", ".xls", ".jpg", ".jpeg"]
    ext = os.path.splitext(value.name)[1].lower()
    if ext not in allowed_extensions:
        raise ValidationError(f'Недопустимый формат файла. Разрешены: {", ".join(allowed_extensions)}')


def validate_file_size(value):
    """Валидация размера файла (макс. 100 МБ)"""
    max_size = 100 * 1024 * 1024  # 100 MB
    if value.size > max_size:
        raise ValidationError(
            f"Размер файла не должен превышать 100 МБ. " f"Текущий размер: {value.size / (1024 * 1024):.1f} МБ"
        )


def document_upload_path(instance, filename):
    """Генерация пути для загрузки файла"""
    return f"documents/{instance.user.id}/{filename}"


class Document(models.Model):
    """Модель загруженного документа"""

    class Status(models.TextChoices):
        PENDING = "pending", "На рассмотрении"
        APPROVED = "approved", "Подтверждён"
        REJECTED = "rejected", "Отклонён"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="documents", verbose_name="Пользователь"
    )
    title = models.CharField(max_length=255, verbose_name="Название документа")
    description = models.TextField(blank=True, verbose_name="Описание")
    file = models.FileField(
        upload_to=document_upload_path, validators=[validate_file_extension, validate_file_size], verbose_name="Файл"
    )
    file_type = models.CharField(max_length=10, verbose_name="Тип файла")
    file_size = models.BigIntegerField(verbose_name="Размер файла (байт)")
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING, verbose_name="Статус")
    admin_comment = models.TextField(blank=True, verbose_name="Комментарий администратора")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    reviewed_at = models.DateTimeField(null=True, blank=True, verbose_name="Дата рассмотрения")

    class Meta:
        verbose_name = "Документ"
        verbose_name_plural = "Документы"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["status"]),
            models.Index(fields=["user", "status"]),
        ]

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.file and not self.file_type:
            ext = os.path.splitext(self.file.name)[1].lower()
            self.file_type = ext
            self.file_size = self.file.size
        super().save(*args, **kwargs)
