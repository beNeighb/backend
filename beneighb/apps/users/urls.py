from django.urls import path

from apps.users.views import ProfileCreateView, SingleProfileView


urlpatterns = [
    path(
        'create-profile/', ProfileCreateView.as_view(), name='create-profile',
    ),
    path(
        'profile/', SingleProfileView.as_view(), name='get-profile',
    ),
]
