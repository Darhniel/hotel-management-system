from rest_framework import serializers
from .models import Booking, BookingLog

class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['customer_name', 'room', 'check_in', 'check_out', 'customer_email']

    def create(self, validated_data):
        user = self.context["request"].user
        hotel = user.hotel if user.is_authenticated else None

        booking = Booking.objects.create(
            hotel=hotel,
            created_by=user if user.is_authenticated else None,
            **validated_data
        )

        BookingLog.objects.create(
            booking=booking,
            action="CREATED",
            performed_by=user if user.is_authenticated else None
        )

        return booking

class BookingLogSerializer(serializers.ModelSerializer):
    performed_by = serializers.SerializerMethodField()

    class Meta:
        model = BookingLog
        fields = [
            "action",
            "performed_by",
            "performed_at",
        ]

    def get_performed_by(self, obj):
        if not obj.performed_by:
            return "Customer"
        return obj.performed_by.email


class OwnerBookingSerializer(serializers.ModelSerializer):
    room = serializers.StringRelatedField()
    logs = BookingLogSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Booking
        fields = [
            "id",
            "room",
            "customer_name",
            "customer_email",
            "check_in",
            "check_out",
            "status",
            "created_by",
            "created_at",
            "cancelled_at",
            "logs",
        ]

    def get_created_by(self, obj):
        if not obj.created_by:
            return "Customer"
        return obj.created_by.email
