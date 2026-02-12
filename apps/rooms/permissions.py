from rest_framework.permissions import BasePermission

class CanViewRooms(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user and not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in [
            "OWNER",
            "MANAGER",
            "FRONT_DESK",
            "HOUSE_KEEPING"
        ]

class CanCheckIn(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user and not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in [
            "MANAGER",
            "FRONT_DESK"
        ]
    
class CanCheckOut(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user and not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in [
            "MANAGER",
            "FRONT_DESK"
        ]
    
class CanCleanRoom(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user and not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in [
            "HOUSE_KEEPING"
        ]

class CanAddRoom(BasePermission):
    def has_permission(self, request, view): # type: ignore
        if not request.user and not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        return request.user.role in [
            "OWNER",
            "MANAGER"
        ]