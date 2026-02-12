from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from .serializers import HotelOwnerRegistrationSerializer

class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser

class RegisterHotelOwnerView(APIView):
    authentication_classes = []
    permission_classes = [IsAuthenticated, IsPlatformAdmin]

    def post(self, request):
        serializer = HotelOwnerRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Hotel Created"}, status=status.HTTP_201_CREATED)