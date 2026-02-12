# LOGIN
"POST /api/v1/auth/login/"
{"username": "sampleowner@gmail.com", "password": "tempPassword123"}
{"username": "frontdesk@renaissancehotel.com", "password": "securePassword123"}

# REFRESH
"POST /api/v1/auth/refresh/"
{"refresh": "<refresh_token>"}

# Get Current User Info
"GET /api/v1/users/me/"

# Reset password
"POST /api/v1/users/reset-password/<token>/"
{
    "new_password": "newSecurePassword456",
    "confirm_password": "newSecurePassword456"
}

# Change password
"POST /api/v1/users/change-password/"
{
    "current_password": "newSecurePassword456",
    "new_password": "newSecurePassword456",
    "confirm_password": "newSecurePassword456"
}

# Forgot Password
"POST /api/v1/users/forgot-password/"
{"email": "email@email.com"}

# Accept Staff Invitation
"POST /api/v1/invites/accept-invite/<token>/"
{
    "password": "securePassword123",
    "first_name": "First Name",
    "last_name": "Last Name",
}

# Accept Hotel Owner Invitation
"POST /api/v1/invites/accept-invite/<token>/"
{
    "password": "securePassword123",
    "first_name": "First Name",
    "last_name": "Last Name",
    "hotel_name": "Hotel Name",
    "hotel_slug": "Hotel-Name",
    "hotel_address": "Hotel Address",
    "hotel_city": "Hotel City",
    "hotel_state": "Hotel State",

}

# Invite Staff Member
"POST /api/v1/invites/invite-staff/"
{"email": "frontdesk@hotel.com", "role": "FRONT_DESK"}

# Invite Hotel Owner
"POST /api/v1/invites/invite-owner/"
{"email": "frontdesk@hotel.com"}

# Revoke Invitation
"POST /api/v1/invites/{id}/revoke/"


# Get List of Rooms
"GET /api/v1/rooms/"

# Add Room (manager/owner only)
"POST /api/v1/rooms/"
{"room_number": "101", "room_type": "DELUXE", "price": 45000}

# Get List of available Rooms
"GET /api/v1/rooms/available/"

# Update Room Status (housekeeping only)
"PATCH /api/v1/rooms/<id>/update-status/"
{"status": "CLEAN"}

# Create Bookings
"POST /api/v1/bookings/"
{
    "room": 1,
    "check_in": "2026-01-20",
    "check_out": "2026-01-22",
    "guest_name": "John Doe",
}

# List Bookings
"GET /api/v1/bookings/"

# Dashboard Summary
"GET /api/v1/dashboard/summary/"

# Revenue Report
"GET /api/v1/dashboard/revenue/?from=2026-01-01&to=2026-01-31"

# Occupancy Report
"GET /api/v1/dashboard/occupancy/?from=2026-01-01&to=2026-01-31"

# Create Booking
"POST /api/v1/bookings/"




{
    "password": "tempPassword123",
    "first_name": "Sample",
    "last_name": "Owner",
    "hotel_name": "The Renaissance Hotel",
    "hotel_slug": "the-hotel-renaissance",
    "hotel_address": "123, Orange Road",
    "hotel_city": "Lagos Mainland",
    "hotel_state": "Lagos"
}
