from rest_framework import serializers
from .models import Invite
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth import get_user_model

User = get_user_model()

class HotelOwnerInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ["email"]

    def create(self, validated_data):
        return Invite.objects.create(
            email=validated_data["email"],
            invite_type="HOTEL_OWNER",
            invited_by=self.context['request'].user,
            expires_at=now() + timedelta(days=7)
        )

class StaffInviteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invite
        fields = ['email', 'role']
        extra_kwargs = {
            "email": {
                "required": True,
                "allow_blank": False,
                "trim_whitespace": True
            },
            "role": {
                "required": True,
                "allow_blank": False
            }
        }

    def validate(self, attrs):
        request = self.context.get("request")
        user = request.user
        email = attrs.get("email", "").strip().lower()
        role = attrs.get("role")

        if not user.hotel:
            raise serializers.ValidationError({"hotel": "You must be associated with a hotel to send requests"})
        
        self._validate_existing_user(email, user.hotel)
        self._validate_role_permissions(user, role)
        self._validate_active_invites(email, user.hotel)

        return attrs
    
    def _validate_role_permissions(self, user, role):
        role_hierachy = {
            "OWNER": ["OWNER", "MANAGER", "FRONT_DESK", "HOUSE_KEEPING"],
            "MANAGER": ["MANAGER", "FRONT_DESK", "HOUSE_KEEPING"]
        }

        allowed_roles = role_hierachy.get(user.role, [])
        if role not in allowed_roles:
            raise serializers.ValidationError({
                "role": f"As a {user.get_role_display()}, you can only invite: {", ".join(allowed_roles)}"
            })
        
    def _validate_active_invites(self, email, hotel):
        active_invites = Invite.objects.filter(
            email__iexact=email,
            hotel=hotel,
            revoked=False,
            is_used=False,
            expires_at__gt=now()
        )

        if active_invites.exists():
            invite = active_invites.first()

            time_remaining = invite.expires_at - now()
            hours = int(time_remaining.total_seconds() / 3600)
            minutes = int((time_remaining.total_seconds() % 3600) / 60)

            if hours > 0:
                time_str = f"{hours} hours"
            else:
                time_str = f"{minutes} minutes"

            raise serializers.ValidationError({
                "detail": 
                    f"An active invite exists for this email. It was sent by {invite.invited_by.get_full_name()} and it expires in {time_str}"
            })
        
    def _validate_existing_user(self, email, hotel):
        existing_user = User.objects.filter(
            email__iexact=email,
            hotel=hotel
        ).first()

        if existing_user:
            raise serializers.ValidationError({
                "email": f"User with email {email} already exist in your hotel."
            })
        

    # def validate_role(self, value):
    #     user = self.context["request"].user

    #     if user.role == "MANAGER" and value in ["MANAGER", "OWNER"]:
    #         raise serializers.ValidationError("Managers cannot invite this role")

    #     return value

    def create(self, validated_data):
        user = self.context['request'].user

        invite = Invite.objects.create(
            email=validated_data["email"].strip().lower(),
            role=validated_data["role"],
            invite_type="STAFF",
            hotel=user.hotel,
            invited_by=user,
            expires_at=now() + timedelta(days=2)
        )

        self._log_invite_creation(invite)

        return invite
    
    def _log_invite_creation(self, invite):
        import logging
        logger = logging.getLogger(__name__)

        logger.info(
            f"Invite created: ID={invite.id}"
            f"Email={invite.email},"
            f"Role={invite.role},"
            f"Hotel={invite.hotel.name if invite.hotel else None},"
            f"Invited By={invite.invited_by.username},"
            f"Expires At={invite.expires_at}"
        )