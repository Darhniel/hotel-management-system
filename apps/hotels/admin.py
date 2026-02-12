from django.contrib import admin
from .models import Hotel
from apps.users.models import User

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ("name", "city", "country", "is_active", "get_owner")
    search_fields = ("name", "city", "country")
    list_filter = ("is_active", "country", "city")
    prepopulated_fields = {"slug": ("name",)}

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "owner":
    #         kwargs["queryset"] = User.objects.filter(role="OWNER")
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @admin.display(description="Owner")
    def get_owner(self, obj):
        owner = User.objects.filter(hotel=obj, role="OWNER").first()
        return owner.username if owner else "No Owner"
    