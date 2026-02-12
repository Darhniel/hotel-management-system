from rest_framework.routers import path
from .views import (
    BookingCreateView,
    BookingCancelView,
    OwnerBookingListView,
    MyBookingsView
)

urlpatterns = [
    path("", BookingCreateView.as_view(), name="booking-create"),
    path("<int:booking_id>/cancel/", BookingCancelView.as_view(), name="booking-cancel"),
    path("owner/", OwnerBookingListView.as_view(), name="owner-bookings"),
    path("mine/", MyBookingsView.as_view(), name="my-bookings"),
]