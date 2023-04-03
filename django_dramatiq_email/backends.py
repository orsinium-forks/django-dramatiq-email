from django.core.mail.backends.base import BaseEmailBackend

from django_dramatiq_email.tasks import send_email
from django_dramatiq_email.utils import email_to_dict


class DramatiqEmailBackend(BaseEmailBackend):
    def __init__(self, fail_silently: bool = False, **kwargs) -> None:
        super().__init__(fail_silently)
        self.init_kwargs = kwargs

    def send_messages(self, email_messages) -> int:
        for message in email_messages:
            send_email.send(email_to_dict(message), self.init_kwargs)
        return len(email_messages)
