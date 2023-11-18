from django.urls import path

from apps.marketplace.views import (
    TaskCreateView,
    TaskForMeListView,
    TaskMineListView,
    TaskRetrieveView,
)


urlpatterns = [
    path(
        'tasks/',
        TaskCreateView.as_view(),
        name='tasks',
    ),
    path(
        'tasks/mine/',
        TaskMineListView.as_view(),
        name='tasks',
    ),
    path(
        'tasks/for-me/',
        TaskForMeListView.as_view(),
        name='tasks',
    ),
    path(
        'tasks/<int:pk>/',
        TaskRetrieveView.as_view(),
        name='task',
    ),
]
