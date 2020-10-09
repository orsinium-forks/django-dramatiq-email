from django.core.mail.backends.base import BaseEmailBackend

from django_dramatiq_email.tasks import send_email
from django_dramatiq_email.utils import email_to_dict


class DramatiqEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        super().__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages):
        result_tasks = []
        for message in email_messages:
            result_tasks.append(
                send_email.send(email_to_dict(message), self.init_kwargs)
            )
        return result_tasks
