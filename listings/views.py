# Create your views here.
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, filters, status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from users.permissions import IsLandlord, IsOwnerOrReadOnly, IsTenant, IsReviewOwnerOrReadOnly
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer

# Класс для просмотра и создания объявлений
class ListingView(generics.ListCreateAPIView):
    #Serializer для конвертации данных объявления в JSON
    serializer_class = ListingSerializer
    # Права доступа для просмотра и создания объявлений
    permission_classes = [IsOwnerOrReadOnly]
    # Фильтры для поиска и сортировки объявлений
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    # Поля для фильтрации объявлений
    filterset_fields = ['price', 'location', 'rooms', 'type', 'is_active']
    # Поля для поиска по объявлениям
    search_fields = ['title', 'description']  # Поиск по заголовкам и описанию
    # Поля для сортировки объявлений
    ordering_fields = ['price', 'created_at']  # Сортировка по цене и дате

    # Метод для получения набора объявлений
    def get_queryset(self):
        # Показ только активных объявлений, если не задано иное
        queryset = Listing.objects.all()
        is_active = self.request.query_params.get('is_active', None)
        if is_active is not None:
            queryset = queryset.filter(is_active=(is_active.lower() == 'true'))
        return queryset

    # Метод для получения прав доступа
    def get_permissions(self):
        if self.request.method == 'POST':
            # Только арендодатели могут добавлять объявления
            self.permission_classes = [IsLandlord]
        else:
            # Все могут просматривать объявления
            self.permission_classes = [IsOwnerOrReadOnly]
        return super().get_permissions()

    # Метод для создания нового объявления
    def perform_create(self, serializer):
        # Устанавливаем текущего пользователя владельцем объявления
        serializer.save(owner=self.request.user)

# Класс для просмотра, обновления и удаления объявления
class ListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Набор объявлений
    queryset = Listing.objects.all()
    # Serializer для конвертации данных объявления в JSON
    serializer_class = ListingSerializer
    # Права доступа для просмотра, обновления и удаления объявления
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # Метод для получения прав доступа
    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            # Только арендодатели могут обновлять и удалять объявления
            self.permission_classes = [IsAuthenticated, IsOwnerOrReadOnly, IsLandlord]
        else:
            # Все могут просматривать объявления
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_context(self):
        return {'request': self.request}


# Класс для просмотра и создания бронирований
class BookingListCreateView(generics.ListCreateAPIView):
    # Serializer для конвертации данных бронирования в JSON
    serializer_class = BookingSerializer
    # Права доступа для просмотра и создания бронирований
    permission_classes = [IsAuthenticated]

    # Метод для получения набора бронирований
    def get_queryset(self):
        # Если пользователь - арендодатель, показать бронирования для его объявлений
        if self.request.user.role == 'landlord':
            return Booking.objects.filter(listing__owner=self.request.user).order_by('-created_at')

        # Если пользователь - арендатор, показать только его бронирования
        elif self.request.user.role == 'tenant':
            return Booking.objects.filter(user=self.request.user).order_by('-created_at')

        # Для остальных случаев - пустой queryset
        return Booking.objects.none()

    # Метод для создания нового бронирования
    def perform_create(self, serializer):
        # Устанавливаем текущего пользователя владельцем бронирования
        serializer.save(user=self.request.user)


# Класс для просмотра, обновления и удаления бронирования
class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Набор бронирований
    queryset = Booking.objects.all()
    # Serializer для конвертации данных бронирования в JSON
    serializer_class = BookingSerializer
    # Права доступа для просмотра, обновления и удаления бронирования
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    # Метод для обновления статуса бронирования
    def patch(self, request, *args, **kwargs):
        booking = self.get_object()
        # Проверка прав арендодателя для подтверждения бронирования
        if booking.listing.owner == request.user:
            if 'status' in request.data and request.data['status'] in ['confirmed', 'cancelled']:
                booking.status = request.data['status']
                booking.save()
                return Response({'message': 'Booking updated successfully'}, status=status.HTTP_200_OK)
        # Проверка на отмену бронирования арендатором
        elif booking.user == request.user and booking.status == 'pending' and request.data.get('status') == 'cancelled':
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': 'Booking cancelled successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Permission denied'}, status=status.HTTP_403_FORBIDDEN)


    # Метод для удаления бронирования
    def delete(self, request, *args, **kwargs):
        # Удаление бронирования (должно разрешаться)
        booking = self.get_object()
        if booking.listing.owner == request.user:
            booking.delete()
            return Response({'message': 'Booking deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        elif booking.can_cancel() and booking.user == request.user:
            booking.status = 'cancelled'
            booking.save()
            return Response({'message': 'Booking cancelled successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Cannot cancel booking'}, status=status.HTTP_403_FORBIDDEN)


# Класс для просмотра, обновления и удаления отзыва
class ReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    # Набор отзывов
    queryset = Review.objects.all()
    # Serializer для конвертации данных отзыва в JSON
    serializer_class = ReviewSerializer
    # Права доступа для просмотра, обновления и удаления отзыва
    permission_classes = [IsAuthenticated, IsReviewOwnerOrReadOnly]

    # Метод для обновления отзыва
    def perform_update(self, serializer):
        # Позволяем обновить отзыв только его автору
        serializer.save(user=self.request.user)

# View для просмотра всех отзывов для конкретного объявления
class ReviewListView(generics.ListAPIView):
    # Serializer для конвертации данных отзыва в JSON
    serializer_class = ReviewSerializer
    # Права доступа для просмотра отзывов
    permission_classes = [IsAuthenticated]

    # Метод для получения набора отзывов
    def get_queryset(self):
        # Возвращаем все отзывы для конкретного объявления
        listing_id = self.kwargs['listing_id']
        return Review.objects.filter(listing_id=listing_id)






