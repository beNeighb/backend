from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from apps.auth0.views import DummyView

urlpatterns = [
    path("dummy/", DummyView.as_view(), name="dummy-view"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
