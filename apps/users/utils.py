from django.contrib.auth.models import Group
from django.core.mail import send_mail
from django.conf import settings

def assign_user_group(user):
    group_map = {
        "OWNER": "Hotel Owners",
        "MANAGER": "Hotel Managers",
        "FRONT_DESK": "Hotel Staff",
        "HOUSEKEEPING": "Hotel Staff",
    }

    group_name = group_map.get(user.role)
    if not group_name:
        return

    group, _ = Group.objects.get_or_create(name=group_name)
    user.groups.add(group)

def send_reset_password_mail(reset, user):
    reset_link = f"{settings.FRONTEND_URL}/reset-password/{reset.token}/"
        
        # Send email
    send_mail(
        subject="Reset Your Password",
        message=f"""
        Hi {user.get_full_name() or user.username},
        
        You requested to reset your password for the Hotel Management System.
        
        Click the link below to reset your password:
        {reset_link}
        
        This link will expire in 1 hour.
        
        If you didn't request this, please ignore this email.
        
        Best regards,
        Hotel Management System Team
        """,
        html_message=f"""
        <h2>Reset Your Password</h2>
        <p>Hi {user.get_full_name() or user.username},</p>
        <p>You requested to reset your password for the Hotel Management System.</p>
        <p><a href="{reset_link}" style="background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
        <p>This link will expire in 1 hour.</p>
        <p>If you didn't request this, please ignore this email.</p>
        <br>
        <p>Best regards,<br>Hotel Management System Team</p>
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )

def send_confirmation_mail(user):
    send_mail(
        subject="Password Reset Successful",
        message=f"""
        Hi {user.get_full_name() or user.username},
        
        Your password has been successfully reset.
        
        If you did not make this change, please contact support immediately.
        
        Best regards,
        Hotel Management System Team
        """,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=False,
    )