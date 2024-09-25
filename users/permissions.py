from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsLandlord(BasePermission):
    """
    Проверяет, что пользователь является арендодателем.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'landlord'

class IsTenant(BasePermission):
    """
    Проверяет, что пользователь является арендатором.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'tenant'

class IsOwnerOrReadOnly(BasePermission):
    """
    Разрешает редактирование только владельцу объекта. Остальные могут только просматривать.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.listing.owner == request.user

class IsReviewOwnerOrReadOnly(BasePermission):
    """
    Разрешение позволяет редактировать и удалять отзыв только его автору. Остальные могут только просматривать.
    """
    def has_object_permission(self, request, view, obj):
        # Проверка прав на уровне объекта: Только автор отзыва может редактировать или удалять
        if request.method in SAFE_METHODS:
            return True
        return obj.user == request.user  # Только автор отзыва может изменять его
