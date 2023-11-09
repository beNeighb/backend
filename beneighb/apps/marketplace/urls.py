from django.urls import path

from apps.marketplace.views import TaskCreateListView, TaskRetrieveView


# TODO: Find a better way to put this urls in one
urlpatterns = [
    path(
        'tasks/',
        TaskCreateListView.as_view(),
        name='tasks',
    ),
    path(
        'tasks/<int:pk>/',
        TaskRetrieveView.as_view(),
        name='task',
    ),
]
