from server.celery import app

from .notifications import send_notification


@app.task()
def send_notification_task(emails: list[str], subject: str, message: str):
    """Задача на отправку уведомления."""
    send_notification(emails=emails, subject=subject, message=message)
