from rest_framework.permissions import BasePermission

class IsManagerOrOwner(BasePermission):
    """
    Custom permission to only allow managers or owners to access certain views.
    """

    def has_permission(self, request, view): # type: ignore
        if request.user.is_superuser:
            return True
        return request.user.is_authenticated and request.user.role in ["OWNER", "MANAGER"]