from django.urls import path, include

from apps.users.views import ProfileCreateView


urlpatterns = [
    path('<int:user_id>/create-profile/', ProfileCreateView.as_view(), name='create-profile'),
]
