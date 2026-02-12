from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Booking, BookingLog
from .serializers import BookingSerializer, OwnerBookingSerializer
from .permissions import CanCancelBooking, CanCreateBooking, CanViewAllBookings
from django.utils.timezone import now


def cancel_booking(booking, user):
    booking.status = "CANCELLED"
    booking.cancelled_at = now()
    booking.save()

    BookingLog.objects.create(
        booking=booking,
        action="CANCELLED",
        performed_by=user
    )
    

class BookingCreateView(APIView):
    permission_classes = [CanCreateBooking]

    def post(self, request):
        serializer = BookingSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data, status=201)
    
class BookingCancelView(APIView):
    permission_classes = [CanCancelBooking]

    def post(self, request, booking_id):
        booking = Booking.objects.get(id=booking_id)
        cancel_booking(booking, request.user)
        return Response({"detail": "Booking cancelled"})
    
class OwnerBookingListView(APIView):
    permission_classes = [CanViewAllBookings]

    def get(self, request):
        bookings = Booking.objects.filter(hotel=request.user.hotel).select_related("room").prefetch_related("logs", "logs__performed_by")
        serializer = OwnerBookingSerializer(bookings, many=True)
        return Response(serializer.data)

class MyBookingsView(APIView):
    def get(self, request):
        if request.user.is_authenticated:
            bookings = Booking.objects.filter(created_by=request.user)
        else:
            email = request.query_params.get("email")
            bookings = Booking.objects.filter(customer_email=email)

        serializer = OwnerBookingSerializer(bookings, many=True)
        return Response(serializer.data)