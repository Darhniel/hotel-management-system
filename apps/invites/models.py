# import uuid
# from django.db import models

# class StaffInvite(models.Model):
#     email = models.EmailField()
#     role = models.CharField(max_length=20)
#     hotel = models.ForeignKey("hotels.Hotel", on_delete=models.CASCADE)
#     token = models.UUIDField(default=uuid.uuid4, unique=True)
#     is_used = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)

import uuid
from django.db import models
from django.conf import settings

class Invite(models.Model):
    INVITE_TYPE_CHOICES = (
        ("HOTEL_OWNER", "Hotel Owner"),
        ("STAFF", "Staff"),
    )

    revoked = models.BooleanField(default=False)

    token = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)

    email = models.EmailField()
    invite_type = models.CharField(max_length=20, choices=INVITE_TYPE_CHOICES)

    hotel = models.ForeignKey(
        "hotels.Hotel",
        null=True,
        blank=True,
        on_delete=models.CASCADE
    )

    role = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    invited_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True
    )

    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} ({self.invite_type})"
