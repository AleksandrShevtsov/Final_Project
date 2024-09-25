# middleware.py
from datetime import datetime
from django.utils.deprecation import MiddlewareMixin
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.exceptions import TokenError

class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware для аутентификации пользователей с помощью JWT-токенов.
    """

    def process_request(self, request):
        """
        Обрабатывает запрос перед тем, как он будет обработан view-функцией.
        """
        # Получаем токены из cookies
        access_token = request.COOKIES.get('access_token')
        refresh_token = request.COOKIES.get('refresh_token')

        if access_token:
            try:
                # Проверяем токен на валидность
                token = AccessToken(access_token)
                # Проверяем, не истек ли токен
                if datetime.utcfromtimestamp(token['exp']) < datetime.utcnow():
                    raise TokenError('Token expired')
                # Если токен валиден, добавляем его в метаданные запроса
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {access_token}'
            except TokenError:
                # Если токен невалиден, обновляем его с помощью refresh-токена
                new_access_token = self.refresh_access_token(refresh_token)
                if new_access_token:
                    # Если обновление токена прошло успешно, добавляем новый токен в метаданные запроса
                    request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                    # Сохраняем новый токен в атрибуте запроса
                    request._new_access_token = new_access_token
                else:
                    # Если обновление токена не прошло успешно, удаляем cookies
                    self.clear_cookies(request)

        elif refresh_token:
            # Если доступный токен не найден, но есть refresh-токен, обновляем доступный токен
            new_access_token = self.refresh_access_token(refresh_token)
            if new_access_token:
                # Если обновление токена прошло успешно, добавляем новый токен в метаданные запроса
                request.META['HTTP_AUTHORIZATION'] = f'Bearer {new_access_token}'
                # Сохраняем новый токен в атрибуте запроса
                request._new_access_token = new_access_token
            else:
                # Если обновление токена не прошло успешно, удаляем cookies
                self.clear_cookies(request)

    def refresh_access_token(self, refresh_token):
        """
        Обновляет доступный токен с помощью refresh-токена.
        """
        try:
            # Обновляем токен
            refresh = RefreshToken(refresh_token)
            return str(refresh.access_token)
        except TokenError:
            # Если обновление токена не прошло успешно, возвращаем None
            return None

    def process_response(self, request, response):
        """
        Обрабатывает ответ после того, как он был обработан view-функцией.
        """
        # Получаем новый токен из атрибута запроса
        new_access_token = getattr(request, '_new_access_token', None)
        if new_access_token:
            # Получаем время истечения нового токена
            access_expiry = AccessToken(new_access_token)['exp']
            # Устанавливаем новый токен в cookies
            response.set_cookie(
                key='access_token',
                value=new_access_token,
                httponly=True,
                secure=False,  # Используйте True для HTTPS
                samesite='Lax',
                expires=datetime.utcfromtimestamp(access_expiry)
            )
        return response

    def clear_cookies(self, request):
        """
        Удаляет cookies с токенами.
        """
        request.COOKIES.pop('access_token', None)
        request.COOKIES.pop('refresh_token', None)