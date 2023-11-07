from django.urls import path

from apps.marketplace.views import TaskCreateView


urlpatterns = [
    path(
        'tasks/', TaskCreateView.as_view(), name='tasks',
    ),
]
