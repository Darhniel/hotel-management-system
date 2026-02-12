from django.urls import path
from .views import RegisterHotelOwnerView

urlpatterns = [
    path('platform/hotels/', RegisterHotelOwnerView.as_view(), name='register-hotel'),
]
