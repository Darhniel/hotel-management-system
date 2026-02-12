from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.http import HttpRequest
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "role",
        "is_staff",
        "is_active",
    )

    def get_queryset(self, request: HttpRequest):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        
        return qs.filter(hotel=request.user.hotel) # type: ignore
    