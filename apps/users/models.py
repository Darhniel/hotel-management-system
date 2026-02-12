import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    ROLE_CHOICES = (
        ("OWNER", "Owner"),
        ("MANAGER", "Manager"),
        ("FRONT_DESK", "Front Desk"),
        ("HOUSE_KEEPING", "House keeping")
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, null=True, blank=True)

    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)

    hotel = models.ForeignKey(
        "hotels.Hotel",
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )

    must_reset_password = models.BooleanField(default=False)

    active_jti = models.CharField(max_length=255, blank=True, null=True)
    session_key = models.CharField(max_length=255, blank=True, null=True, unique=True)
    last_session_update = models.DateTimeField(null=True, blank=True)


class PasswordResetToken(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_tokens"
    )
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    used_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['token', 'expires_at', 'is_used']),
        ]
    
    def is_valid(self):
        now = timezone.now()
        return not self.is_used and self.expires_at > now