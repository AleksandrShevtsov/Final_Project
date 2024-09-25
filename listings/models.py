from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone

from users.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


# Модель объявления
class Listing(models.Model):
    # Варианты типов объявлений
    TYPE_CHOICES = [
        ('apartment', 'Apartment'),  # Квартира
        ('house', 'House'),  # Дом
        ('studio', 'Studio'),  # Студия
    ]

    # Владелец объявления (связь с моделью User)
    owner = models.ForeignKey(User, related_name='listings', on_delete=models.CASCADE)

    # Заголовок объявления
    title = models.CharField(max_length=255)

    # Описание объявления
    description = models.TextField()

    # Местоположение объявления
    location = models.CharField(max_length=255)

    # Цена объявления
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # Количество комнат в объявлении
    rooms = models.IntegerField()

    # Тип объявления (выбор из TYPE_CHOICES)
    type = models.CharField(choices=TYPE_CHOICES, max_length=20)

    # Активность объявления (по умолчанию True)
    is_active = models.BooleanField(default=True)

    # Дата создания объявления (автоматически устанавливается при создании)
    created_at = models.DateTimeField(auto_now_add=True)

    # Дата обновления объявления (автоматически устанавливается при обновлении)
    updated_at = models.DateTimeField(auto_now=True)

    # Возвращает строковое представление объявления (заголовок)
    def __str__(self):
        return self.title


# Модель бронирования
class Booking(models.Model):
    # Варианты статусов бронирования
    STATUS_CHOICES = [
        ('pending', 'Pending'),  # Ожидание подтверждения арендодателем
        ('confirmed', 'Confirmed'),  # Подтверждено арендодателем
        ('canceled', 'Canceled'),  # Отменено пользователем или арендодателем
    ]

    # Объявление, на которое сделано бронирование (связь с моделью Listing)
    listing = models.ForeignKey(Listing, related_name='bookings', on_delete=models.CASCADE)

    # Пользователь, сделавший бронирование (связь с моделью User)
    user = models.ForeignKey(User, related_name='bookings', on_delete=models.CASCADE)

    # Дата начала бронирования
    start_date = models.DateField()

    # Дата окончания бронирования
    end_date = models.DateField()

    # Статус бронирования (выбор из STATUS_CHOICES, по умолчанию 'pending')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    # Дата создания бронирования (автоматически устанавливается при создании)
    created_at = models.DateTimeField(auto_now_add=True)

    # Возвращает строковое представление бронирования (имя пользователя и заголовок объявления)
    def __str__(self):
        return f'Booking by {self.user.email} for {self.listing.title}'

    # Метод для проверки возможности отмены бронирования
    def can_cancel(self):
        # Проверка, можно ли отменить бронирование (до начала бронирования)
        return self.start_date > timezone.now().date()


# Модель отзыва
class Review(models.Model):
    # Объявление, на которое оставлен отзыв (связь с моделью Listing)
    listing = models.ForeignKey(Listing, related_name='reviews', on_delete=models.CASCADE)

    # Пользователь, оставивший отзыв (связь с моделью User)
    user = models.ForeignKey(User, related_name='reviews', on_delete=models.CASCADE)

    # Оценка объявления (целое число от 1 до 5)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])

    # Комментарий к отзыву
    comment = models.TextField()

    # Дата создания отзыва (автоматически устанавливается при создании)
    created_at = models.DateTimeField(auto_now_add=True)

    # Meta-класс для обеспечения уникальности отзыва для каждого пользователя и объявления
    class Meta:
        unique_together = ('listing', 'user')  # Ensures one review per user per listing

    # Возвращает строковое представление отзыва (заголовок объявления и имя пользователя)
    def __str__(self):
        return f'Review for {self.listing.title} by {self.user.email}'