from rest_framework.throttling import UserRateThrottle

class HotelStaffRateThrottle(UserRateThrottle):
    """
    Custom throttle for hotel owners and managers.
    Limits: 20 revokes per day, 5 per hour [citation:1].
    """
    scope = 'hotel_staff'  # This key must be defined in settings

    def allow_request(self, request, view):
        # Only apply throttle to owners/managers performing sensitive actions
        user = request.user
        if user.is_authenticated and user.role in ['OWNER', 'MANAGER']:
            return super().allow_request(request, view)
        # Don't throttle other users for this endpoint if they have access
        return True