from bookings.models import Booking

def is_room_available(room, check_in, check_out):
    return not Booking.objects.filter(
        room=room,
        status__in=["confirmed", "checked_in"],
        check_in__lt=check_out,
        check_out__gt=check_in
    ).exists()
