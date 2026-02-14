from django.urls import path
from .views import (
    RoomCreateView,
    RoomListView,
    RoomCheckInView,
    RoomCheckOutView,
    RoomCleanedView,
    test_email
)

urlpatterns = [
    path("", RoomListView.as_view()),
    path("test-email/", test_email),
    path("add", RoomCreateView.as_view()),
    path("<int:room_id>/check-in/", RoomCheckInView.as_view()),
    path("<int:room_id>/check-out/", RoomCheckOutView.as_view()),
    path("<int:room_id>/cleaned/", RoomCleanedView.as_view()),
]