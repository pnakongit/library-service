from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from user.views import UserCreateAPIView, UserManageAPIView

urlpatterns = [
    path("", UserCreateAPIView.as_view(), name="user_create"),
    path("me/", UserManageAPIView.as_view(), name="me"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]

app_name = "user"
