from django.core.mail import send_mail
from django.conf import settings

def send_invite_email(invite):
    link = f"{settings.FRONTEND_URL}/accept-invite/{invite.token}/"

    send_mail(
        subject="You're invited",
        message=f"Complete your registration: {link}",
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[invite.email],
    )


def send_revocation_email(invite):
    """
    Sends an email notification that an invite has been revoked [citation:2].
    """
    subject = "Your Invitation Has Been Revoked"
    
    message = f"""
    Hello,

    Your invitation to join {invite.hotel.name} as a {invite.get_role_display()} has been revoked by the hotel administration.

    This means the invitation link you received is no longer valid.

    If you believe this is an error, please contact the hotel directly.

    Best regards,
    {invite.hotel.name} Management Team
    """
    
    html_message = f"""
    <html>
    <body>
        <p>Hello,</p>
        <p>Your invitation to join <strong>{invite.hotel.name}</strong> as a <strong>{invite.get_role_display()}</strong> has been revoked by the hotel administration.</p>
        <p>This means the invitation link you received is no longer valid.</p>
        <p>If you believe this is an error, please contact the hotel directly.</p>
        <br>
        <p>Best regards,<br>
        <strong>{invite.hotel.name} Management Team</strong></p>
    </body>
    </html>
    """
    
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[invite.email],
            fail_silently=False,
            html_message=html_message
        )
        return True
    except Exception as e:
        print(f"Failed to send revocation email: {e}")
        return False