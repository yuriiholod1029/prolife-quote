import logging
from collections import defaultdict
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

WELCOME_EMAIL = {
    'subject': 'Welcome to Prolife!',
    'message': '',
    'template_name': 'welcome_email',
}

ORDER_CREATED_EMAIL = {
    'subject': 'Reign Wholesale Order placed {order_id} by {sales_rep_id}',
    'message': '',
    'template_name': 'order_created_email',
}


class EmailService:
    def __init__(self, email_config):
        self.email_config = email_config

    def format_text(self, text, **kwargs):
        format_kwargs = defaultdict(str, kwargs)
        return text.format_map(format_kwargs)

    def send(self, to_emails, cc_emails, from_email=None, **kwargs):
        if not to_emails:
            logger.info("Not sending email because no destination emails.")
            return
        subject = self.format_text(self.email_config['subject'], **kwargs)
        template_name = self.email_config['template_name']
        if template_name is None:
            msg_plain = self.format_text(self.email_config['message'], **kwargs)
            msg_html = None
        else:
            msg_plain = render_to_string(f'core/email/{template_name}.txt', context=kwargs)
            msg_html = render_to_string(f'core/email/{template_name}.html', context=kwargs)
        from_email = from_email or settings.DEFAULT_FROM_EMAIL
        logger.info("Sending email...")
        msg = EmailMultiAlternatives(subject, msg_plain, from_email, to=to_emails, cc=cc_emails or [])
        msg.attach_alternative(msg_html, "text/html")
        msg.send()