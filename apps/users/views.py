from typing import cast, TYPE_CHECKING

from apps.users.models import PasswordResetToken
if TYPE_CHECKING:
    from apps.users.models import User

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from apps.invites.models import Invite
from django.contrib.auth import get_user_model
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from .utils import send_reset_password_mail, send_confirmation_mail

# Create your views here.
class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        data = {
            "id": user.id,
            "username": user.username,
            "email": user.email
        }
        return Response(data)

class HotelTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        # Store current session jti
        user.active_jti = self.get_token(user)["jti"]  # type: ignore
        user.save(update_fields=["active_jti"]) # type: ignore

        return data

class HotelTokenView(TokenObtainPairView):
    serializer_class = HotelTokenSerializer

class AcceptInviteView(APIView):
    def post(self, request, token):
        invite = Invite.objects.get(token=token, is_used=False)

        user = User.objects.create_user(
            username=invite.email,
            email=invite.email,
            password=request.data["password"],
            role=invite.role,
            hotel=invite.hotel
        )

        invite.is_used = True
        invite.save()

        return Response({"detail": "Account Created"})

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        current_password = request.data.get("current_password")
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")

        if not all([current_password, new_password, confirm_password]):
            return Response(
                {"detail": "All fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {"detail": "New passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = request.user

        if not user.check_password(current_password):
            return Response(
                {"message": "Current password is incorrect"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if current_password == new_password:
            return Response(
                {"message": "New password must be different from current password"},
                status=status.HTTP_400_BAD_REQUEST
            )

        errors = self._validate_password_strength(new_password)
        if errors:
            return Response(
                {"message": "Password validation failed", "errors": errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.must_reset_password = False
        user.save()

        return Response(
            {"detail": "Password changed successful"},
            status=status.HTTP_200_OK
        )
    
    def _validate_password_strength(self, password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters")
        
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one number")
        
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter")
        
        return errors


User = get_user_model()

class ForgotPasswordView(APIView):
    """Step 1: User requests password reset"""
    
    def post(self, request):
        email = request.data.get("email")
        
        if not email:
            return Response(
                {"detail": "Email is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Clean email
        email = email.strip().lower()
        
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            # Security: Don't reveal if user exists
            return Response(
                {"detail": "If an account exists with this email, you will receive a password reset link."},
                status=status.HTTP_200_OK
            )
        
        # Check if user already has active reset tokens
        active_tokens = PasswordResetToken.objects.filter(
            user=user,
            is_used=False,
            expires_at__gt=timezone.now()
        )
        
        # Invalidate existing tokens
        active_tokens.update(is_used=True)
        
        # Create new reset token
        reset_token = PasswordResetToken.objects.create(
            user=user,
            expires_at=timezone.now() + timedelta(hours=1)  # 1 hour expiry
        )

        send_reset_password_mail(reset_token, user)
        
        return Response(
            {"detail": "If an account exists with this email, you will receive a password reset link."},
            status=status.HTTP_200_OK
        )

class ResetPasswordView(APIView):
    """Step 2: User resets password with token"""
    
    def post(self, request, token):
        new_password = request.data.get("new_password")
        confirm_password = request.data.get("confirm_password")
        
        if not new_password or not confirm_password:
            return Response(
                {"detail": "Both password fields are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {"detail": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        password_errors = self._validate_password_strength(new_password)
        if password_errors:
            return Response(
                {"detail": "Password validation failed", "errors": password_errors},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            return Response(
                {"detail": "Invalid or expired reset token"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = reset_token.user
        
        if user.check_password(new_password):
            return Response(
                {"detail": "New password cannot be the same as old password"},
                status=status.HTTP_400_BAD_REQUEST
            )
        

        user.set_password(new_password)
        user.must_reset_password = False
        user.save()
        
        reset_token.is_used = True
        reset_token.used_at = timezone.now()
        reset_token.save()

        send_confirmation_mail(user)
        
        return Response(
            {"detail": "Password has been reset successfully"},
            status=status.HTTP_200_OK
        )
    
    def _validate_password_strength(self, password):
        """Validate password strength"""
        errors = []
        
        if len(password) < 8:
            errors.append("Password must be at least 8 characters long")
        
        if not any(char.isdigit() for char in password):
            errors.append("Password must contain at least one number")
        
        if not any(char.isupper() for char in password):
            errors.append("Password must contain at least one uppercase letter")
        
        if not any(char.islower() for char in password):
            errors.append("Password must contain at least one lowercase letter")
        
        return errors
    