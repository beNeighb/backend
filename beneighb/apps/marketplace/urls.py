from django.urls import path

from apps.marketplace.views import TaskView


# TODO: Find a better way to put this urls in one
urlpatterns = [
    path(
        'tasks/<int:pk>/',
        TaskView.as_view(),
        name='task',
    ),
    path(
        'tasks/',
        TaskView.as_view(),
        name='tasks',
    ),
]
