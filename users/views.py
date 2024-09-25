from datetime import datetime

from django.contrib.auth import authenticate
from django_filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from users.serializers import RegisterUserSerializer, UserListSerializer, LoginSerializer
from .models import User


# Класс для вывода списка пользователей.
class UserListGenericView(ListAPIView):
    # Права доступа для этого класса.
    permission_classes = [IsAuthenticated, IsAdminUser]
    # Serializer для вывода списка пользователей.
    serializer_class = UserListSerializer
    # Queryset для вывода списка пользователей.
    queryset = User.objects.all()
    # Бэкенды для фильтрации и сортировки.
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    # Поля для фильтрации.
    filterset_fields = ['username', 'email']  # Замените на ваши поля фильтрации
    # Поля для сортировки.
    ordering_fields = ['username', 'email']  # Замените на ваши поля сортировки
    # Поле по умолчанию для сортировки.
    ordering = ['username']  # Поле по умолчанию для сортировки

    # Метод для вывода списка пользователей.
    def list(self, request, *args, **kwargs):
        # Получить queryset пользователей.
        users = self.get_queryset()
        # Если пользователей нет, вернуть пустой список.
        if not users.exists():
            return Response(data=[], status=status.HTTP_204_NO_CONTENT)
        # Serializer для вывода списка пользователей.
        serializer = self.get_serializer(users, many=True)
        # Вернуть список пользователей.
        return Response(serializer.data, status=status.HTTP_200_OK)


# Класс для регистрации нового пользователя.
class RegisterUserGenericView(CreateAPIView):
    # Serializer для регистрации нового пользователя.
    serializer_class = RegisterUserSerializer
    # Права доступа для этого класса.
    permission_classes = [AllowAny]

    # Метод для создания нового пользователя.
    def create(self, request, *args, **kwargs):
        # Serializer для регистрации нового пользователя.
        serializer = self.get_serializer(data=request.data)
        # Валидация данных пользователя.
        serializer.is_valid(raise_exception=True)
        # Создать нового пользователя.
        user = serializer.save()
        # Вернуть ответ с данными пользователя.
        response = Response(serializer.data, status=status.HTTP_201_CREATED)
        # Установить JWT токены в куки.
        set_jwt_cookies(response, user)
        # Вернуть ответ.
        return response


# Класс для авторизации пользователя.
class LoginView(APIView):
    # Права доступа для этого класса.
    permission_classes = [AllowAny]
    # Serializer для авторизации пользователя.
    serializer_class = LoginSerializer

    # Метод для авторизации пользователя.
    def post(self, request, *args, **kwargs):
        # Аутентификация пользователя.
        user = authenticate(request, username=request.data.get('email'), password=request.data.get('password'))
        # Если пользователь аутентифицирован, вернуть ответ с JWT токенами.
        if user:
            response = Response(status=status.HTTP_200_OK)
            set_jwt_cookies(response, user)
            return response
        # Если пользователь не аутентифицирован, вернуть ответ с ошибкой.
        return Response({"detail": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)


# Класс для выхода пользователя.
class LogoutView(APIView):
    # Права доступа для этого класса.
    permission_classes = [IsAuthenticated]

    # Метод для выхода пользователя при GET запросе.
    def get(self, request, *args, **kwargs):
        # Выход пользователя.
        return self.logout_user(request)

    # Метод для выхода пользователя при POST запросе.
    def post(self, request, *args, **kwargs):
        # Выход пользователя.
        return self.logout_user(request)

    # Метод для выхода пользователя.
    def logout_user(self, request):
        # Очистка куков и завершение сессии пользователя.
        request.session.flush()  # Полностью очищаем сессию пользователя
        # Создаем ответ для клиента.
        response = Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)

        # Удаляем токены из куков.
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')

        return response


# Класс для вывода защищенных данных.
class ProtectedDataView(APIView):
    # Права доступа для этого класса.
    permission_classes = [IsAuthenticated]

    # Метод для вывода защищенных данных.
    def get(self, request):
        return Response({"message": "Hello, authenticated user!", "user": request.user.username})


# Функция для установки JWT токенов в куки.
def set_jwt_cookies(response, user):
    # Создать refresh токен.
    refresh_token = RefreshToken.for_user(user)
    # Создать access токен.
    access_token = refresh_token.access_token
    # Время истечения access токена.
    access_expiry = datetime.utcfromtimestamp(access_token['exp'])
    # Время истечения refresh токена.
    refresh_expiry = datetime.utcfromtimestamp(refresh_token['exp'])
    # Установить access токен в куки.
    response.set_cookie(key='access_token', value=str(access_token), httponly=True, secure=False, samesite='Lax', expires=access_expiry)
    # Установить refresh токен в куки.
    response.set_cookie(key='refresh_token', value=str(refresh_token), httponly=True, secure=False, samesite='Lax', expires=refresh_expiry)