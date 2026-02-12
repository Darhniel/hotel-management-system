from django.urls import path
from .views import (
    RoomCreateView,
    RoomListView,
    RoomCheckInView,
    RoomCheckOutView,
    RoomCleanedView
)

urlpatterns = [
    path("", RoomListView.as_view()),
    path("add", RoomCreateView.as_view()),
    path("<int:room_id>/check-in/", RoomCheckInView.as_view()),
    path("<int:room_id>/check-out/", RoomCheckOutView.as_view()),
    path("<int:room_id>/cleaned/", RoomCleanedView.as_view()),
]