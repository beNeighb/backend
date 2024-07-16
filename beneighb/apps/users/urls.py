from django.urls import path

from apps.users.views import (
    ProfileBlockView,
    ProfileCreateView,
    MyProfileView,
    ProfileView,
)


urlpatterns = [
    path(
        'create-profile/',
        ProfileCreateView.as_view(),
        name='create-profile',
    ),
    path(
        'profile/',
        MyProfileView.as_view(),
        name='get-my-profile',
    ),
    path(
        'profiles/<int:pk>/',
        ProfileView.as_view(),
        name='profile-detail',
    ),
    path(
        'profiles/<int:pk>/block/',
        ProfileBlockView.as_view(),
        name='profile-block',
    ),
]
