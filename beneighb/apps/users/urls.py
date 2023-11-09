from django.urls import path

from apps.users.views import ProfileCreateView, MyProfileView, ProfileView


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
        name='get-profile',
    ),
]
