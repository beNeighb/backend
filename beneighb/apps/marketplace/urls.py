from django.urls import path

from apps.marketplace.views import (
    OfferCreateView,
    TaskCreateView,
    TaskForMeListView,
    TaskMineListView,
    TaskRetrieveView,
    TaskWithMyOfferListView,
)


urlpatterns = [
    path(
        'tasks/',
        TaskCreateView.as_view(),
        name='create-task',
    ),
    path(
        'tasks/mine/',
        TaskMineListView.as_view(),
        name='tasks-mine',
    ),
    path(
        'tasks/for-me/',
        TaskForMeListView.as_view(),
        name='tasks-for-me',
    ),
    path(
        'tasks/with-my-offer/',
        TaskWithMyOfferListView.as_view(),
        name='tasks-for-me',
    ),
    path(
        'tasks/<int:pk>/',
        TaskRetrieveView.as_view(),
        name='task',
    ),
    path(
        'offers/',
        OfferCreateView.as_view(),
        name='create-offer',
    ),
]
