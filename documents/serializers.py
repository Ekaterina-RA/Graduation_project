from rest_framework import serializers
from .models import Document


class DocumentListSerializer(serializers.ModelSerializer):
    """Сериализатор для списка документов"""

    username = serializers.CharField(source="user.username", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    file_size_display = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = ["id", "title", "file_type", "file_size_display", "status", "status_display", "username", "created_at"]

    def get_file_size_display(self, obj):
        size = obj.file_size
        if size < 1024:
            return f"{size} Б"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} КБ"
        else:
            return f"{size / (1024 * 1024):.1f} МБ"


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Сериализатор для загрузки документа"""

    file = serializers.FileField(
        help_text="Файл документа. Допустимые форматы: DWG, PDF, DOCX, XLSX, JPG. Макс. 100 МБ."
    )

    class Meta:
        model = Document
        fields = ["id", "title", "description", "file"]

    def validate_file(self, value):
        if not value:
            raise serializers.ValidationError("Файл обязателен для загрузки")
        return value


class DocumentDetailSerializer(serializers.ModelSerializer):
    """Сериализатор для детального просмотра"""

    username = serializers.CharField(source="user.username", read_only=True)
    user_email = serializers.EmailField(source="user.email", read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)
    file_url = serializers.SerializerMethodField()

    class Meta:
        model = Document
        fields = [
            "id",
            "title",
            "description",
            "file",
            "file_url",
            "file_type",
            "file_size",
            "status",
            "status_display",
            "admin_comment",
            "username",
            "user_email",
            "created_at",
            "updated_at",
            "reviewed_at",
        ]
        read_only_fields = ["status", "admin_comment", "reviewed_at"]

    def get_file_url(self, obj):
        if obj.file:
            request = self.context.get("request")
            if request:
                return request.build_absolute_uri(obj.file.url)
        return None


class DocumentReviewSerializer(serializers.Serializer):
    """Сериализатор для подтверждения/отклонения"""

    action = serializers.ChoiceField(choices=["approve", "reject"])
    comment = serializers.CharField(required=False, allow_blank=True)
