from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_admin_new_document(self, document_id):
    """Уведомление администратору о новом документе"""
    try:
        from .models import Document

        document = Document.objects.select_related("user").get(id=document_id)

        admin_emails = User.objects.filter(is_staff=True).values_list("email", flat=True)

        if not admin_emails:
            return f"No admin users found for document {document_id}"

        subject = f"📄 Новый документ: {document.title}"
        message = (
            f"Здравствуйте!\n\n"
            f"Пользователь {document.user.get_full_name() or document.user.username} "
            f"загрузил новый документ.\n\n"
            f"📋 Название: {document.title}\n"
            f"📁 Тип файла: {document.file_type}\n"
            f"📏 Размер: {document.file_size / (1024 * 1024):.1f} МБ\n"
            f'📅 Дата загрузки: {document.created_at.strftime("%d.%m.%Y %H:%M")}\n\n'
            f'Описание: {document.description or "Не указано"}\n\n'
            f"Пожалуйста, рассмотрите документ в панели администратора."
        )

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=list(admin_emails),
            fail_silently=False,
        )

        return f"Admin notification sent for document {document_id}"

    except Exception as exc:
        # Повторная попытка при ошибке
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_user_document_reviewed(self, document_id, action_type):
    """Уведомление пользователю о рассмотрении документа"""
    try:
        from .models import Document

        document = Document.objects.select_related("user").get(id=document_id)

        user_email = document.user.email
        if not user_email:
            return f"User has no email for document {document_id}"

        action_text = "подтверждён ✅" if action_type == "approve" else "отклонён ❌"

        subject = f'📄 Ваш документ "{document.title}" {action_text}'

        if action_type == "approve":
            message = (
                f"Здравствуйте, {document.user.get_full_name() or document.user.username}!\n\n"
                f'Ваш документ "{document.title}" был подтверждён администратором.\n\n'
                f'Дата рассмотрения: {document.reviewed_at.strftime("%d.%m.%Y %H:%M")}\n'
            )
            if document.admin_comment:
                message += f"\nКомментарий: {document.admin_comment}\n"
        else:
            message = (
                f"Здравствуйте, {document.user.get_full_name() or document.user.username}!\n\n"
                f'К сожалению, ваш документ "{document.title}" был отклонён.\n\n'
                f'Дата рассмотрения: {document.reviewed_at.strftime("%d.%m.%Y %H:%M")}\n'
            )
            if document.admin_comment:
                message += f"\nПричина отклонения: {document.admin_comment}\n"
            message += "\nВы можете загрузить исправленную версию документа."

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user_email],
            fail_silently=False,
        )

        return f"User notification sent for document {document_id}"

    except Exception as exc:
        raise self.retry(exc=exc)
