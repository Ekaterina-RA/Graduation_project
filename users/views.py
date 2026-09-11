from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from .serializers import RegisterSerializer, UserSerializer

from drf_spectacular.utils import extend_schema

@extend_schema(
    summary='Регистрация нового пользователя',
    description='Создаёт нового пользователя и возвращает токен авторизации.',
    tags=['users'],
)


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя"""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = Token.objects.get(user=user)
        return Response(
            {'token': token.key, 'user': UserSerializer(user).data},
            status=status.HTTP_201_CREATED
        )

@extend_schema(
    summary='Авторизация',
    description='Получение токена по email/username и паролю.',
    tags=['users'],
)


class LoginView(ObtainAuthToken):
    """Получение токена авторизации"""
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        token = Token.objects.get(key=response.data['token'])
        user_data = UserSerializer(token.user).data
        return Response({'token': token.key, 'user': user_data})

@extend_schema(
    summary='Профиль пользователя',
    description='Просмотр и редактирование данных текущего пользователя.',
    tags=['users'],
)


class ProfileView(generics.RetrieveUpdateAPIView):
    """Просмотр и редактирование профиля"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user