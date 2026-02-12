from django.db import models
from apps.rooms.models import Room
from django.conf import settings

# class Booking(models.Model):
#     STATUS_CHOICES = (
#         ("BOOKED", "Booked"),
#         ("CHECKED_IN", "Checked In"),
#         ("CHECKED_OUT", "Checked Out"),
#         ("CANCELLED", "Cancelled"),
#     )

#     customer_name = models.CharField(max_length=100)
#     hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE)
#     room = models.ForeignKey(Room, on_delete=models.CASCADE)
#     check_in_date = models.DateField(db_index=True)
#     check_out_date = models.DateField(db_index=True)
#     status = models.CharField(max_length=15, choices=STATUS_CHOICES)
#     total_amount = models.DecimalField(max_digits=10, decimal_places=2)


class Booking(models.Model):
    STATUS_CHOICES = (
        ("CONFIRMED", "Confirmed"),
        ("CANCELLED", "Cancelled"),
        ("CHECKED_IN", "Checked In"),
        ("CHECKED_OUT", "Checked Out"),
    )

    hotel = models.ForeignKey(
        "hotels.Hotel",
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    room = models.ForeignKey(
        "rooms.Room",
        on_delete=models.PROTECT
    )

    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()

    check_in = models.DateField(null=True, blank=True)
    check_out = models.DateField(null=True, blank=True)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="CONFIRMED"
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_bookings"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f"{self.customer_name} - {self.room}"


class BookingLog(models.Model):
    ACTION_CHOICES = (
        ("CREATED", "Created"),
        ("CANCELLED", "Cancelled"),
        ("UPDATED", "Updated"),
    )

    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name="logs"
    )

    action = models.CharField(max_length=20, choices=ACTION_CHOICES)

    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )

    performed_at = models.DateTimeField(auto_now_add=True)