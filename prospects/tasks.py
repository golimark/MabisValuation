from time import sleep
from django.core.mail import EmailMessage
from django.conf import settings
from celery import shared_task
from celery.utils.log import get_task_logger

logger = get_task_logger(__name__)


@shared_task
def send_email_task(subject, email_address, message):
    """Sends an email when the feedback form has been submitted."""
    # sleep()  # Simulate expensive operation(s) that freeze Django
   
    email = EmailMessage(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email_address],
    )
    email.send(fail_silently=False)