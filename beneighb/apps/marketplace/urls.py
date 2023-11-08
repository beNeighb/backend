from django.urls import path

from apps.marketplace.views import TaskView


urlpatterns = [
    path(
        'tasks/<int:pk>/',
        TaskView.as_view(),
        name='tasks',
    ),
]
