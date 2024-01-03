from django.urls import path

from apps.marketplace.views import (
    ChatMineListView,
    OfferCreateView,
    OfferAcceptView,
    OfferMineListView,
    TaskCreateView,
    TaskForMeListView,
    TaskMineListView,
    TaskRetrieveView,
    TaskWithMyOfferListView,
)


# TODO: Split urls into separate files
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
    path(
        'offers/<int:pk>/accept/',
        OfferAcceptView.as_view(),
        name='accept-offer',
    ),
    path(
        'offers/mine/',
        OfferMineListView.as_view(),
        name='offers-mine',
    ),
    path(
        'chats/',
        ChatMineListView.as_view(),
        name='chats-mine',
    ),
]
