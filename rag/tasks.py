# tasks.py
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from .models import ChatHistory

logger = logging.getLogger(__name__)

scheduler = BackgroundScheduler()

# ------------------ Task 1: Delete old chat history ------------------ #
def delete_old_chat_history(days: int = 0, hours: int = 0, minutes: int = 0):
    """
    Delete chat history older than the specified time.

    Args:
        days (int): Number of days.
        hours (int): Number of hours.
        minutes (int): Number of minutes.
    """
    cutoff = timezone.now() - timedelta(days=days, hours=hours, minutes=minutes)
    old_chats = ChatHistory.objects.filter(created_at__lt=cutoff)
    count = old_chats.count()
    old_chats.delete()
    logger.info(f"Deleted {count} old chat messages older than {cutoff}")


# ------------------ Task 2: Send verification email ------------------ #
def send_verification_email(user):
    """Send verification email to the user."""
    try:
        send_mail(
            subject="Verify your account",
            message=f"Hello {user.username}, please verify your email to activate your account.",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )
        logger.info(f"Sent verification email to {user.email}")
    except Exception as e:
        logger.error(f"Failed to send verification email to {user.email}: {e}")


# ------------------ Scheduler Setup ------------------ #
def start_scheduler():
    # For testing: delete messages older than 1 minutes
    scheduler.add_job(lambda: delete_old_chat_history(minutes=1),
                      'interval', minutes=1, id='delete_old_chats')
    scheduler.start()
    logger.info("APScheduler started.")
