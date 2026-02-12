from rest_framework.permissions import BasePermission

class IsPlatformAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_superuser


class IsHotelOwner(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if user.is_superuser:
            return True
        return user.role == "OWNER"
    
class CanInviteStaff(BasePermission):
    def has_permission(self, request, view): # type: ignore
        user = request.user
        return user.role in ["OWNER", "MANAGER"]
