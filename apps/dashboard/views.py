from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.bookings.models import Booking
from apps.rooms.models import Room
from apps.users.permissions import IsOwner, SingleSessionPermission
from .permissions import IsManagerOrOwner

class DashboardSummaryView(APIView):
    permission_classes = [
        IsManagerOrOwner, 
        IsAuthenticated, 
        SingleSessionPermission
    ]  

    def get(self, request):
        total_rooms = Room.objects.count()
        occupied_rooms = Room.objects.filter(status="OCCUPIED").count()
        data = {
            "total_bookings": Booking.objects.count(),
            "occupied_rooms": occupied_rooms,
            "available_rooms": total_rooms - occupied_rooms,
            "occupancy_rate": round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0,
        }
        
        return Response(data)

# class RevenueSummaryView(APIView):
#     permission_classes = [
#         IsOwner, 
#         IsAuthenticated, 
#         SingleSessionPermission
#     ]  

#     def get(self, request):
#         total_rooms = Room.objects.count()
#         occupied_rooms = Room.objects.filter(status="OCCUPIED").count()
#         data = {
#             "total_bookings": Booking.objects.count(),
#             "occupied_rooms": occupied_rooms,
#             "available_rooms": total_rooms - occupied_rooms,
#             "occupancy_rate": round((occupied_rooms / total_rooms * 100), 1) if total_rooms > 0 else 0,
#         }
        
#         return Response(data)