from django.db import models
from django.contrib.auth import get_user_model
from apps.users.models import User

# User = get_user_model()

class Room(models.Model):
    STATUS_CHOICES = (
        ("AVAILABLE", "Available"),
        ("OCCUPIED", "Occupied"),
        ("CLEANING", "Requires Cleaning"),
    )

    id = models.AutoField(primary_key=True)
    hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE)
    room_number = models.CharField(max_length=10, unique=True)
    room_type = models.CharField(max_length=50)
    price_per_night = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="AVAILABLE")
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("hotel", "room_number")

    def __str__(self):
        return f"Room {self.room_number} - {self.room_type}"

    def save(self, *args, **kwargs):
        # Check if this is an existing room
        if self.pk:
            # Get the old room from database
            old_room = Room.objects.get(pk=self.pk)
            
            # Check if status changed
            if old_room.status != self.status:
                # Create log entry
                RoomStatusLog.objects.create(
                    room=self,
                    previous_status=old_room.status,
                    new_status=self.status,
                    changed_by=getattr(self, '_changed_by', None)  # You need to set this
                )
        
        super().save(*args, **kwargs)

class RoomStatusLog(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name="status_logs")
    old_status = models.CharField(max_length=20)
    new_status = models.CharField(max_length=20)

    changed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True
    )

    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-changed_at"]
