from rest_framework import serializers
from .models import Room, RoomStatusLog

class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = ['id', 'hotel', 'room_number', 'room_type', 'price_per_night', 'status', 'is_active']
        read_only_fields = ['id', 'hotel', 'status']

class RoomStatusLogSerializer(serializers.ModelSerializer):
    changed_by = serializers.SerializerMethodField()
    room_number = serializers.CharField(source="room.room_number", read_only=True)

    class Meta:
        model = RoomStatusLog
        fields = [
            "id",
            "room_number",
            "old_status",
            "new_status",
            "changed_by",
            "changed_at"
        ]

    def get_changed_by_name(self, obj):
        if obj.changed_by:
            return obj.changed_by.get_full_name() or obj.changed_by.username
        return "System"
