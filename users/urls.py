from django.urls import path
from .views import (UserListGenericView, RegisterUserGenericView, ProtectedDataView,
                    LoginView, LogoutView)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


urlpatterns = [
    path('', UserListGenericView.as_view()),
    path('register/', RegisterUserGenericView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('protected/', ProtectedDataView.as_view(), name='protected_data'),


]
