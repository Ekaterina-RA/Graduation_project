from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from django.contrib.auth import get_user_model, authenticate
from drf_spectacular.utils import extend_schema
from .serializers import RegisterSerializer, UserSerializer, LoginSerializer

User = get_user_model()


@extend_schema(
    summary="Регистрация нового пользователя",
    description="Создаёт нового пользователя и возвращает токен авторизации.",
    tags=["users"],
)
class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Получаем токен
        token = Token.objects.get(user=user)
        return Response({"token": token.key, "user": UserSerializer(user).data}, status=status.HTTP_201_CREATED)


@extend_schema(
    summary="Авторизация",
    description="Получение токена по email/username и паролю.",
    tags=["users"],
    request=LoginSerializer,  # 2. Явно указываем сериализатор запроса для Swagger!
    responses={
        200: {"type": "object", "properties": {"token": {"type": "string"}, "user": {"type": "object"}}},
        400: {"type": "object", "properties": {"error": {"type": "string"}}},
    },
)
class LoginView(APIView):
    """Вход по username ИЛИ email"""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        validated_data = serializer.validated_data
        username = validated_data.get("username")
        email = validated_data.get("email")
        password = validated_data.get("password")

        user = None

        # Пробуем искать по username
        if username:
            user = authenticate(username=username, password=password)

        # Если не нашли — пробуем по email
        if user is None and email:
            try:
                user_obj = User.objects.get(email=email)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass

        if user is None:
            return Response({"error": "Неверные учётные данные"}, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user": UserSerializer(user).data,  # 4. Используем UserSerializer для единообразия ответа
            }
        )


@extend_schema(
    summary="Профиль пользователя",
    description="Просмотр и редактирование данных текущего пользователя.",
    tags=["users"],
)
class ProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля"""

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
