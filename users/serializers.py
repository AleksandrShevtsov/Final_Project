from rest_framework import serializers
from users.models import User
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re

# Serializer для вывода списка пользователей.
class UserListSerializer(serializers.ModelSerializer):
    # Serializer для вывода списка пользователей.

    # Метакласс для конфигурации serializer.
    class Meta:
        # Модель, для которой создан serializer.
        model = User
        # Поля, которые будут выводиться в serializer.
        fields = (
            # Имя пользователя.
            'username',
            # Email пользователя.
            'email',
            # Дата последнего входа пользователя.
            'last_login',
        )


# Serializer для вывода информации о пользователе.
class UserSerializer(serializers.ModelSerializer):
    # Serializer для вывода информации о пользователе.

    # Метакласс для конфигурации serializer.
    class Meta:
        # Модель, для которой создан serializer.
        model = User
        # Поля, которые будут выводиться в serializer.
        fields = [
            # Email пользователя.
            'email',
            # Роль пользователя.
            'role',
            # Пароль пользователя.
            'password'
        ]
        # Дополнительные параметры для полей.
        extra_kwargs = {
            # Пароль пользователя доступен только для записи.
            'password': {'write_only': True}
        }

    # Метод для создания нового пользователя.
    def create(self, validated_data):
        # Создать нового пользователя.
        user = User.objects.create_user(**validated_data)
        return user


# Serializer для регистрации нового пользователя.
class RegisterUserSerializer(serializers.ModelSerializer):
    # Serializer для регистрации нового пользователя.

    # Поле для подтверждения пароля.
    re_password = serializers.CharField(max_length=128, write_only=True)

    # Метакласс для конфигурации serializer.
    class Meta:
        # Модель, для которой создан serializer.
        model = User
        # Поля, которые будут выводиться в serializer.
        fields = [
            # Имя пользователя.
            'username',
            # Email пользователя.
            'email',
            # Роль пользователя.
            'role',
            # Пароль пользователя.
            'password',
            # Подтверждение пароля.
            're_password'
        ]
        # Дополнительные параметры для полей.
        extra_kwargs = {
            # Пароль пользователя доступен только для записи.
            'password': {'write_only': True}
        }

    # Метод для валидации данных пользователя.
    def validate(self, data):
        # Валидация данных пользователя.
        # Проверка имени пользователя.
        if not re.match("^[a-zA-Z0-9_]*$", data.get('username')):
            raise serializers.ValidationError("Имя пользователя должно быть алфавитно-цифровым или содержать _")

        # Проверка пароля.
        if data.get('password') != data.get('re_password'):
            raise serializers.ValidationError("Пароли не совпадают")

        # Проверка пароля на соответствие требованиям.
        try:
            validate_password(data.get("password"))
        except ValidationError as err:
            raise serializers.ValidationError({"password": err.messages})

        return data

    # Метод для создания нового пользователя.
    def create(self, validated_data):
        # Создать нового пользователя.
        password = validated_data.pop('password')
        validated_data.pop('re_password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


# Serializer для авторизации пользователя.
class LoginSerializer(serializers.Serializer):
    # Serializer для авторизации пользователя.

    # Email пользователя.
    email = serializers.EmailField(
        max_length=100,
        style={'placeholder': 'Email', 'autofocus': True}
    )
    # Пароль пользователя.
    password = serializers.CharField(
        max_length=100,
        style={'input_type': 'password', 'placeholder': 'Пароль'}
    )
    # Запомнить меня.
    remember_me = serializers.BooleanField()