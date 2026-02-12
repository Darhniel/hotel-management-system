import jwt
from django.conf import settings
from django.core.cache import cache
from rest_framework.permissions import BasePermission
from rest_framework.request import Request
from rest_framework.views import APIView

class IsOwner(BasePermission): 
    """
    Custom permission to only allow owners of an object to access it.
    """
    def has_permission(self, request: Request, view: APIView):
        user = request.user
        if user.is_superuser:
            return True
        return user.is_authenticated and user.role == "OWNER"
    
class IsManager(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool: # type: ignore
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role in ["MANAGER", "OWNER"]
    
class IsFrontDesk(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool: # type: ignore
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role in ["FRONT_DESK", "MANAGER", "OWNER"]
    
class IsHouseKeeping(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool: # type: ignore
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role == "HOUSE_KEEPING"

class SingleSessionPermission(BasePermission):
    def has_permission(self, request: Request, view: APIView) -> bool: # type: ignore
        # token = request.auth
        user = request.user

        if not user.is_authenticated:
            return False

        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return False
        
        token = auth_header.split(" ")[1]

        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            token_session_key = payload.get("session_key")
            
            return token_session_key == user.session_key
        except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
            return False

        # return token.get("jti") == user.active_jti
    
class MustResetPassword(BasePermission):
    def has_permission(self, request, view) -> bool: # type: ignore
        if not request.user.is_authenticated:
            return True
        return not request.user.must_reset_password