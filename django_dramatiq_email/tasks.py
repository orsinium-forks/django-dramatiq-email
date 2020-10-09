# Based on https://github.com/pmclanahan/django-celery-email/
# Copyright (c) 2010, Paul McLanahan
# All rights reserved.
import logging

import dramatiq
from django.conf import settings
from django.core.mail import get_connection

from django_dramatiq_email.utils import dict_to_email, email_to_dict

TASK_CONFIG = {
    "actor_name": "django_dramatiq_email_send_emails",
    "queue_name": "django_email",
}
TASK_CONFIG.update(settings.DRAMATIQ_EMAIL_TASK_CONFIG)


@dramatiq.actor(**TASK_CONFIG)
def send_email(message, backend_kwargs=None):
    message = email_to_dict(message)
    backend_kwargs = backend_kwargs or {}
    conn = get_connection(backend=settings.DRAMATIQ_EMAIL_BACKEND, **backend_kwargs)
    try:
        conn.open()
    except Exception:
        logging.exception("Cannot reach backend %s", settings.DRAMATIQ_EMAIL_BACKEND)

    sent = conn.send_messages([dict_to_email(message)])
    logging.debug("Successfully sent email message to %r.", message["to"])

    conn.close()
    return sent
