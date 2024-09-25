from django.contrib.auth.models import PermissionsMixin, AbstractBaseUser, BaseUserManager
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    # Менеджер пользователей, наследующийся от BaseUserManager.

    def create_user(self, email, password=None, **extra_fields):
        # Создает нового пользователя.
        #     ValueError: Если email не указан.
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        # Создает суперпользователя.

        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    # Модель пользователя.

    ROLE_CHOICES = [
        ('tenant', 'Tenant'),  # Арендатор
        ('landlord', 'Landlord'),  # Арендодатель
    ]

    username = models.CharField(
        _("username"),
        max_length=50,
        unique=True,
        error_messages={
            "unique": _("A user with that username already exists."),
        }
    )
    # Имя пользователя.

    email = models.EmailField(
        _("email address"),
        max_length=150,
        unique=True
    )
    # Email пользователя.

    is_staff = models.BooleanField(default=False)
    # Флаг, указывающий, является ли пользователь адмистратором.

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='tenant')
    # Роль пользователя.

    is_active = models.BooleanField(default=True)
    # Флаг, указывающий, активен ли пользователь.

    date_joined = models.DateTimeField(
        name="registered", auto_now_add=True
    )
    # Дата регистрации пользователя.

    last_login = models.DateTimeField(null=True, blank=True)
    # Дата последнего входа пользователя.

    updated_at = models.DateTimeField(auto_now=True)
    # Дата последнего обновления пользователя.

    deleted_at = models.DateTimeField(null=True, blank=True)
    # Дата удаления пользователя.

    deleted = models.BooleanField(default=False)
    # Флаг, указывающий, удален ли пользователь.

    USERNAME_FIELD = "email"
    # Поле, используемое в качестве имени пользователя.

    REQUIRED_FIELDS = [
        "username",
    ]
    # Обязательные поля при создании пользователя.

    objects = UserManager()
    # Менеджер пользователей.

    def __str__(self):
        # Возвращает строковое представление пользователя.
        return f"{self.username}"