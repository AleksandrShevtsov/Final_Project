from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from rest_framework import serializers
from .models import Listing, Booking, Review


# Сериализатор для модели Review
class ReviewSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Review.
    Проверяет, что пользователь бронировал это объявление, прежде чем он может оставить отзыв.
    """
    class Meta:
        # Модель, которую сериализует этот класс
        model = Review
        # Поля, которые сериализуются
        fields = ['id', 'listing', 'user', 'rating', 'comment', 'created_at']
        # Поля, которые доступны только для чтения
        read_only_fields = ['user', 'created_at']

    def validate(self, data):
        """
        Проверяет, что пользователь бронировал это объявление.
        """
        # Пользователь, который пытается оставить отзыв
        user = self.context['request'].user
        # Объявление, на которое пользователь пытается оставить отзыв
        listing = data['listing']
        # Бронирование, которое пользователь сделал на это объявление
        booking = Booking.objects.filter(user=user, listing=listing, status='confirmed')
        # Если бронирование не найдено, то пользователь не может оставить отзыв
        if not booking.exists():
            raise serializers.ValidationError("Вы можете оставить отзыв только после завершения бронирования.")
        return data

# Сериализатор для модели Booking
class BookingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Booking.
    Проверяет корректность дат бронирования и пересечение дат с другими бронированиями.
    """
    class Meta:
        # Модель, которую сериализует этот класс
        model = Booking
        # Все поля модели сериализуются
        fields = '__all__'
        # Поля, которые доступны только для чтения
        read_only_fields = ['user', 'created_at']

    def validate(self, data):
        """
        Проверяет корректность дат бронирования и пересечение дат с другими бронированиями.
        """
        # Проверка корректности дат бронирования
        if data['start_date'] >= data['end_date']:
            raise serializers.ValidationError("End date must be after start date.")

        # Проверка пересечения дат только для создания и подтверждения бронирования
        if self.instance:
            # Если бронирование уже существует, проверяем статус
            if self.instance.status == 'pending' and data.get('status') == 'confirmed':
                # Объявление, на которое пользователь сделал бронирование
                listing = data.get('listing', self.instance.listing)
                # Бронирования, которые пересекаются с текущим бронированием
                overlapping_bookings = Booking.objects.filter(
                    listing=listing,
                    status='confirmed',  # Проверяем только подтвержденные бронирования
                    start_date__lt=data['end_date'],
                    end_date__gt=data['start_date']
                ).exclude(id=self.instance.id)

                # Если найдены пересекающиеся бронирования, то текущее бронирование не может быть подтверждено
                if overlapping_bookings.exists():
                    raise serializers.ValidationError("Эти даты уже забронированы.")
        else:
            # Для новых бронирований проверяем пересечение с подтвержденными
            # Объявление, на которое пользователь сделал бронирование
            listing = data['listing']
            # Бронирования, которые пересекаются с текущим бронированием
            overlapping_bookings = Booking.objects.filter(
                listing=listing,
                status='confirmed',  # Проверяем только подтвержденные бронирования
                start_date__lt=data['end_date'],
                end_date__gt=data['start_date']
            )

            # Если найдены пересекающиеся бронирования, то текущее бронирование не может быть подтверждено
            if overlapping_bookings.exists():
                raise serializers.ValidationError("Эти даты уже забронированы.")

        return data

# Сериализатор для модели Listing
class ListingSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Listing.
    Сериализует отзывы и бронирования, связанные с объявлением.
    """
    reviews = ReviewSerializer(many=True, read_only=True)
    bookings = serializers.SerializerMethodField()  # Кастомное поле для бронирований

    class Meta:
        model = Listing
        exclude = ['owner']  # Исключаем поле owner
        read_only_fields = ['is_active']

    def get_bookings(self, obj):
        """
        Фильтруем бронирования в зависимости от пользователя:
        - Арендатор видит только свои бронирования.
        - Арендодатель видит все бронирования для своих объявлений.
        """
        request = self.context.get('request')  # Получаем запрос из контекста

        if request and hasattr(request, 'user'):
            user = request.user

            # Если пользователь аутентифицирован
            if user.is_authenticated:
                # Если пользователь - арендодатель (владелец объявления)
                if user == obj.owner:
                    return BookingSerializer(obj.bookings.all(), many=True).data

                # Если пользователь - арендатор
                elif user.role == 'tenant':
                    return BookingSerializer(obj.bookings.filter(user=user), many=True).data

        # Если пользователь не аутентифицирован или нет доступа, возвращаем пустой список
        return []

