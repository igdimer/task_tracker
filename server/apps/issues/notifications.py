from django.conf import settings
from django.core.mail import send_mail


def send_notification(emails: list[str], subject: str, message: str) -> None:
    """Send notification to emails."""
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=emails,
    )
