from django.urls import include, path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from apps.auth0.views import (
    BeneighbPasswordResetConfirmView,
    BeneighbPasswordResetView,
    DummyView,
    GoogleLoginView,
)

# namespace ↓ (view names need to be prefixed with 'auth0:')
# app_name = 'auth0'

urlpatterns = [
    path('dummy/', DummyView.as_view(), name='dummy-view'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('password-reset/', BeneighbPasswordResetView.as_view()),
    path(
        'password-reset-confirm/<uidb64>/<token>/',
        BeneighbPasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
    # TODO: Remove the ones we don't need
    path('registration/', include('dj_rest_auth.registration.urls')),
    path("login/google/", GoogleLoginView.as_view(), name="google_login"),
    # path('accounts/', include('allauth.urls')),
]
