from celery.utils.log import get_task_logger

from prolife.celery import app
from prolife.core.email_service import EmailService

logger = get_task_logger(__name__)


@app.task
def send_email(email_config, to_list, cc_list, custom_kwargs, from_email=None):
    email_service = EmailService(email_config)
    email_service.send(
        to_list,
        cc_list,
        from_email=from_email,
        **custom_kwargs,
    )
