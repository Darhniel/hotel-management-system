from datetime import timedelta

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Invite
from .serializers import StaffInviteSerializer, HotelOwnerInviteSerializer
from apps.users.permissions import SingleSessionPermission
from .permissions import IsPlatformAdmin, IsHotelOwner, CanInviteStaff
from .utils import send_invite_email, send_revocation_email
from .throttles import HotelStaffRateThrottle
from django.utils.timezone import now
from apps.hotels.models import Hotel
import uuid
from django.contrib.auth import get_user_model
from apps.users.utils import assign_user_group
from django.shortcuts import get_object_or_404

User = get_user_model()

class InviteHotelOwnerView(APIView):
    permission_classes = [IsPlatformAdmin, SingleSessionPermission]

    def post(self, request):
        serializer = HotelOwnerInviteSerializer(
            data=request.data,
            context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        invite = serializer.save()

        send_invite_email(invite)

        return Response({"detail": "Invite sent"})

class InviteStaffView(APIView):
    permission_classes = [IsAuthenticated, SingleSessionPermission, CanInviteStaff]

    def post(self, request):
        serializer = StaffInviteSerializer(
            data=request.data, 
            context={"request": request}
        )
        
        if serializer.is_valid():
            user = request.user
            last_24_hours = now() - timedelta(hours=24)

            invites_last_24h = Invite.objects.filter(
                invited_by=user,
                created_at=last_24_hours
            ).count()

            if invites_last_24h >= 20:
                return Response({
                    "detail": "Daily invite limit reached. You can send up to send 20 invites per day."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            invite = serializer.save()
            send_invite_email(invite)
            
            return Response(
                {
                    "detail": "Invite sent successfully",
                    "invite": {
                        "id": invite.id,
                        "email": invite.email
                    }
                }, 
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AcceptInviteView(APIView):
    permission_classes = []

    def post(self, request, token):
        invite = Invite.objects.filter(
            token=token,
            is_used=False,
            revoked=False,
            expires_at__gt=now()
        ).first()

        if not invite:
            return Response({"detail": "Invalid or expired invite"}, status=status.HTTP_400_BAD_REQUEST)

        password = request.data.get("password")
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        hotel_name = request.data.get("hotel_name")
        hotel_slug = request.data.get("hotel_slug")
        hotel_address = request.data.get("hotel_address")
        hotel_city = request.data.get("hotel_city")
        hotel_state = request.data.get("hotel_state")

        if invite.invite_type == "HOTEL_OWNER":
            hotel = Hotel.objects.create(
                name=hotel_name,
                slug=hotel_slug,
                address=hotel_address,
                city=hotel_city,
                state=hotel_state
            )
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=invite.email,
                email=invite.email,
                password=password,
                role="OWNER",
                hotel=hotel,
                is_staff=False,
                is_superuser=False,
                must_reset_password=True
            )
        else:  # STAFF invite
            user = User.objects.create_user(
                first_name=first_name,
                last_name=last_name,
                username=invite.email,
                email=invite.email,
                password=password,
                role=invite.role,
                hotel=invite.hotel,
                is_staff=False,
                is_superuser=False,
                must_reset_password=True
            )

        assign_user_group(user)
        invite.is_used = True
        invite.save()

        return Response({"detail": "Account created successfully"}, status=status.HTTP_201_CREATED)

class RevokeInviteView(APIView):
    permission_classes = [IsAuthenticated, SingleSessionPermission, IsHotelOwner]
    throttle_classes = [HotelStaffRateThrottle]

    def post(self, request, id):
        invite = get_object_or_404(
            Invite,
            id=id,
            hotel=request.user.hotel
        )

        if not invite:
            return Response(
                {"detail": "Invalid invite"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invite.is_used:
            return Response(
                {"detail": "Can't revoke an invite that's already been used"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invite.revoked:
            return Response(
                {"detail": "Invite is already revoked"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if invite.expires_at < now():
            return Response(
                {"detail": "Invite is already expired"},
                status=status.HTTP_400_BAD_REQUEST
            )

        invite.revoked = True
        invite.save()

        email_sent = send_revocation_email(invite)

        return Response(
            {
                "detail": "Invite revoked successfully", 
                "email_notification_sent": email_sent
            },
            status=status.HTTP_200_OK
        )
    
class ResendInviteView(APIView):
    permission_classes = [IsAuthenticated, SingleSessionPermission, IsHotelOwner]
    throttle_classes = [HotelStaffRateThrottle]

    def post(self, request, id):
        invite = get_object_or_404(
            Invite,
            id=id,
            hotel=request.user.hotel
        )

        if not invite:
            return Response(
                {"detail": "Invalid invite"}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        if invite.is_used:
            return Response(
                {"detail": "Cannot resend an invite that has already been accepted"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invite.revoked:
            return Response(
                {"detail": "Cannot resend a revoked invite. Please create a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if invite.expires_at > now():
            return Response(
                {"detail": "Invite is still valid. No need to resend."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        existing_active_invites = Invite.objects.filter(
            email__iexact=invite.email,
            hotel=request.user.hotel,
            is_used=False,
            revoked=False,
            expires_at__gt=now()  # Still active
        ).exclude(id=invite.id) 
        
        if existing_active_invites.exists():
            return Response(
                {"detail": "An active invite already exists for this email"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        
        new_token = uuid.uuid4()
        new_expiry = now() + timedelta(days=2)

        new_invite = Invite.objects.create(
            email=invite.email,
            role=invite.role,
            invite_type=invite.invite_type,
            hotel=invite.hotel,
            invited_by=request.user,
            token=new_token,
            expires_at=new_expiry,
            revoked=False,
            is_used=False
        )

        invite = new_invite
        invite.save()

        send_invite_email(invite)

        return Response(
            {"detail": "Invite resent successfully"}, 
            status=status.HTTP_200_OK
        )