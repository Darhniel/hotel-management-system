from django.db import models
from django.conf import settings

class Hotel(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)

    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100, default="Nigeria")

    phone = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)

    currency = models.CharField(max_length=10, default="NGN")

    owner = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="owned_hotel",
        null=True,
        blank=True
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
