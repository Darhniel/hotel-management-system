from ..models import RoomStatusLog

def update_room_status(room, new_status, user):
    if room.status == new_status:
        return

    RoomStatusLog.objects.create(
        room=room,
        old_status=room.status,
        new_status=new_status,
        changed_by=user
    )

    room.status = new_status
    room.save(update_fields=["status"])
