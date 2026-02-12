from django.urls import path
from .views import InviteHotelOwnerView, InviteStaffView, AcceptInviteView, RevokeInviteView

urlpatterns = [
    path('invite-owner/', InviteHotelOwnerView.as_view(), name='invite-owner'),
    path('invite-staff/', InviteStaffView.as_view(), name='invite-staff'),
    path("accept-invite/<uuid:token>/", AcceptInviteView.as_view(), name="accept-invite"),
    path('<int:id>/revoke-invite/', RevokeInviteView.as_view(), name='revoke-invite'),
]
