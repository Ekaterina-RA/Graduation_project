from django.contrib import admin
from django.utils.html import format_html
from .models import Document
from .tasks import notify_user_document_reviewed


@admin.action(description="✅ Подтвердить выбранные документы")
def approve_documents(modeladmin, request, queryset):
    """Массовое подтверждение документов"""
    from django.utils import timezone

    pending_docs = queryset.filter(status=Document.Status.PENDING)
    count = pending_docs.count()

    for doc in pending_docs:
        doc.status = Document.Status.APPROVED
        doc.reviewed_at = timezone.now()
        doc.save()
        # Асинхронное уведомление пользователя
        notify_user_document_reviewed.delay(doc.id, "approve")

    modeladmin.message_user(request, f"Подтверждено документов: {count}")


@admin.action(description="❌ Отклонить выбранные документы")
def reject_documents(modeladmin, request, queryset):
    """Массовое отклонение документов"""
    from django.utils import timezone

    pending_docs = queryset.filter(status=Document.Status.PENDING)
    count = pending_docs.count()

    for doc in pending_docs:
        doc.status = Document.Status.REJECTED
        doc.reviewed_at = timezone.now()
        doc.save()
        notify_user_document_reviewed.delay(doc.id, "reject")

    modeladmin.message_user(request, f"Отклонено документов: {count}")


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Админ-панель для управления документами"""

    list_display = ["title", "user", "file_type", "file_size_display", "status_badge", "created_at", "reviewed_at"]
    list_filter = ["status", "file_type", "created_at"]
    search_fields = ["title", "description", "user__username", "user__email"]
    readonly_fields = ["created_at", "updated_at", "reviewed_at", "file_size"]
    actions = [approve_documents, reject_documents]
    date_hierarchy = "created_at"
    list_per_page = 25

    fieldsets = (
        ("Основная информация", {"fields": ("title", "description", "user", "file")}),
        ("Информация о файле", {"fields": ("file_type", "file_size"), "classes": ("collapse",)}),
        ("Статус и рассмотрение", {"fields": ("status", "admin_comment", "reviewed_at")}),
        ("Даты", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def status_badge(self, obj):
        """Цветной бейдж статуса"""
        colors = {
            "pending": "#f59e0b",
            "approved": "#10b981",
            "rejected": "#ef4444",
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 10px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display(),
        )

    status_badge.short_description = "Статус"

    def file_size_display(self, obj):
        """Человекочитаемый размер файла"""
        size = obj.file_size
        if size < 1024:
            return f"{size} Б"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} КБ"
        return f"{size / (1024 * 1024):.1f} МБ"

    file_size_display.short_description = "Размер"
