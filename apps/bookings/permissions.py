from rest_framework.permissions import BasePermission
    
class CanCreateBooking(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user.is_authenticated:
            return True 
        return request.user.role in ["MANAGER", "FRONT_DESK"]


class CanCancelBooking(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user.is_authenticated:
            return True 
        return request.user.role in ["MANAGER", "FRONT_DESK"]


class CanViewAllBookings(BasePermission):
    def has_permission(self, request, view): # type: ignore
        return request.user.role in ["OWNER", "MANAGER", "FRONT_DESK"]