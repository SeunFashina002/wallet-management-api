from django.urls import path
from .views import UserRegister, UserLogin
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/login/', UserLogin.as_view(), name='token_obtain_pair'),
    path('auth/login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),   
    path('auth/register/', UserRegister.as_view(), name='register_user'),
]