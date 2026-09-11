from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Document
from .serializers import (
    DocumentListSerializer, DocumentUploadSerializer,
    DocumentDetailSerializer, DocumentReviewSerializer
)
from .tasks import notify_admin_new_document, notify_user_document_reviewed


class IsOwnerOrAdmin(permissions.BasePermission):
    """Разрешение: владелец или администратор"""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user or request.user.is_staff
from drf_spectacular.utils import (
    extend_schema, extend_schema_view, OpenApiParameter, OpenApiResponse
)

@extend_schema_view(
    list=extend_schema(
        summary='Список документов',
        description='Получить список всех документов. '
                    'Пользователь видит только свои, админ — все.',
        tags=['documents'],
        parameters=[
            OpenApiParameter(
                name='status',
                type=str,
                description='Фильтр по статусу: pending, approved, rejected'
            ),
            OpenApiParameter(
                name='search',
                type=str,
                description='Поиск по названию и описанию'
            ),
        ],
    ),
    create=extend_schema(
        summary='Загрузить документ',
        description='Загрузка нового документа. '
                    'Поддерживаемые форматы: DWG, PDF, DOCX, XLSX, JPG. '
                    'Максимальный размер: 100 МБ. '
                    'После загрузки администратор получает уведомление по email.',
        tags=['documents'],
    ),
    retrieve=extend_schema(
        summary='Детали документа',
        description='Получить полную информацию о документе.',
        tags=['documents'],
    ),
    review=extend_schema(
        summary='Рассмотреть документ (только админ)',
        description='Подтвердить или отклонить документ. '
                    'После рассмотрения пользователь получает уведомление по email.',
        tags=['documents'],
        request={
            'application/json': {
                'type': 'object',
                'properties': {
                    'action': {'type': 'string', 'enum': ['approve', 'reject']},
                    'comment': {'type': 'string'},
                },
                'required': ['action'],
            }
        },
        responses={
            200: OpenApiResponse(description='Документ успешно рассмотрен'),
            403: OpenApiResponse(description='Доступ запрещён (не админ)'),
        },
    ),
)

class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet для управления документами"""
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'file_type']
    search_fields = ['title', 'description']
    ordering_fields = ['created_at', 'title', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Document.objects.all()
        return Document.objects.filter(user=user)

    def get_serializer_class(self):
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'create':
            return DocumentUploadSerializer
        elif self.action == 'review':
            return DocumentReviewSerializer
        return DocumentDetailSerializer

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        # Отправляем уведомление админу через Celery
        notify_admin_new_document.delay(document.id)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAdminUser])
    def review(self, request, pk=None):
        """Подтверждение или отклонение документа (для админа)"""
        document = self.get_object()
        serializer = DocumentReviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        action_type = serializer.validated_data['action']
        comment = serializer.validated_data.get('comment', '')

        from django.utils import timezone

        if action_type == 'approve':
            document.status = Document.Status.APPROVED
        else:
            document.status = Document.Status.REJECTED

        document.admin_comment = comment
        document.reviewed_at = timezone.now()
        document.save()

        # Уведомляем пользователя через Celery
        notify_user_document_reviewed.delay(document.id, action_type)

        return Response(
            DocumentDetailSerializer(document, context={'request': request}).data
        )