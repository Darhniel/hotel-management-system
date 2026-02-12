# from django.db.models import Q
# from datetime import datetime
from datetime import datetime
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import status
# from rest_framework.decorators import action
from rest_framework.response import Response
# from rest_framework.permissions import IsAuthenticated

from apps.bookings.models import Booking
from apps.rooms.services.status import update_room_status
from .models import Room
from .serializers import RoomSerializer, RoomStatusLogSerializer
from .permissions import CanAddRoom, CanCheckIn, CanCheckOut, CanViewRooms, CanCleanRoom
from apps.users.permissions import IsFrontDesk, IsManager, IsHouseKeeping, IsOwner
from apps.rooms.services.status import update_room_status

class RoomCreateView(APIView):
    permission_classes = [CanAddRoom]

    def post(self, request):
        serializer = RoomSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(hotel=request.user.hotel)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RoomListView(APIView):
    permission_classes = [CanViewRooms]

    def get(self, request):
        rooms = Room.objects.filter(hotel=request.user.hotel)
        serializer = RoomSerializer(rooms, many=True)
        return Response(serializer.data)

class RoomCheckInView(APIView):
    permission_classes = [CanCheckIn]

    def post(self, request, room_id):
        booking_id = request.data.get("booking_id")

        booking = Booking.objects.get(id=booking_id, room_id=room_id)

        if booking.status == "CANCELLED":
            return Response(
                {"detail": "Cannot check in cancelled booking"},
                status=status.HTTP_400_BAD_REQUEST
            )

        room = booking.room
        update_room_status(room, "OCCUPIED", request.user)
        room.save()

        booking.status = "CHECKED_IN"
        booking.save()

        return Response({"detail": "Checked in"})

class RoomCheckOutView(APIView):
    permission_classes = [CanCheckOut]

    def post(self, request, room_id):
        room = Room.objects.get(id=room_id, hotel=request.user.hotel)

        update_room_status(room, "CLEANING", request.user)
        room.save()

        return Response({"detail": "Checked out"})

class RoomCleanedView(APIView):
    permission_classes = [CanCleanRoom]

    def post(self, request, room_id):
        room = Room.objects.get(
            id=room_id,
            hotel=request.user.hotel,
            status="CLEANING"
        )

        update_room_status(room, "AVAILABLE", request.user)
        room.save()

        return Response({"detail": "Room is now available"})
    

class RoomAvailabilityView(APIView):
    permission_classes = [IsOwner | IsManager | IsFrontDesk | IsHouseKeeping]

    def get(self, request):
        check_in = request.query_params.get("check_in")
        check_out = request.query_params.get("check_out")

        if not check_in or not check_out:
            return Response(
                {"detail": "Both check in and check out parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
            check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

            if check_in_date >= check_out_date:
                return Response(
                    {"detail": "check out must be after check in."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Use YYYY-MM-DD"},
                status=status.HTTP_400_BAD_REQUEST
            )

        conflicting_bookings = Booking.objects.filter(
            hotel=request.user.hotel,
            status__in=["CONFIRMED", "CHECKED_IN"],
            check_in__lt=check_out_date,
            check_out__gt=check_in_date,
        )

        available_rooms = Room.objects.filter(
            hotel=request.user.hotel,
            status="AVAILABLE"
        ).exclude(
            id__in=conflicting_bookings.values_list("room_id", flat=True)
        )

        serializer = RoomSerializer(available_rooms, many=True)

        response_data = {
            "count": available_rooms.count(),
            "check_in": check_in,
            "check_out": check_out,
            "hotel": request.user.hotel.name,
            "rooms": serializer.data
        }

        return Response(response_data)

class RoomAuditLogView(APIView):
    permission_classes = [IsOwner]

    def get(self, request, id):
        room = get_object_or_404(
            Room, id=id, hotel=request.user.hotel
        )

        logs = room.status_logs.all() # type: ignore
        serializer = RoomStatusLogSerializer(logs, many=True)
        return Response(serializer.data)


# class RoomViewSet(ModelViewSet):
#     queryset = Room.objects.all()
#     serializer_class = RoomSerializer
#     permission_classes = [IsAuthenticated, CanViewRooms]

#     @action(detail=False, methods=['get'], permission_classes=[IsFrontDesk | IsHouseKeeping])
#     def available_rooms(self,request):
#         check_in = request.query_params.get('check_in_date')
#         check_out = request.query_params.get('check_out_date')
#         if not check_in or not check_out:
#             return Response({"error": "Please provide check_in_date and check_out_date"}, status=400)
        
#         check_in_date = datetime.strptime(check_in, "%Y-%m-%d").date()
#         check_out_date = datetime.strptime(check_out, "%Y-%m-%d").date()

#         booked_rooms = Booking.objects.filter(
#             Q(check_in_date__lt=check_out_date) & Q(check_out_date__gt=check_in_date)
#         ).values_list('room_id', flat=True)

#         available_rooms = Room.objects.exclude(id__in=booked_rooms)
#         room_data = RoomSerializer(available_rooms, many=True).data
        
#         return Response(room_data)
    
#     @action(detail=True, methods=['patch'], permission_classes=[IsHouseKeeping])
#     def update_status(self, request, pk=None):
#         room = self.get_object()
#         room.status = request.data.get('status')
#         room.save()
#         return Response({"status": room.status})