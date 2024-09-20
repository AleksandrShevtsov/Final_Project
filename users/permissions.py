from rest_framework import permissions

class IsAdminUser(permissions.BasePermission):
    """
    Разрешение позволяет доступ только администраторам.
    """

    def has_permission(self, request, view):
        # Проверяем, является ли пользователь администратором и активным
        return request.user and request.user.is_staff and request.user.is_active
