from django.urls import path

from apps.users.views import ProfileCreateView


urlpatterns = [
    path(
        'create-profile/', ProfileCreateView.as_view(), name='create-profile'
    ),
]
