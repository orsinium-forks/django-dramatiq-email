import json
import os.path
from email.mime.image import MIMEImage

import pytest
from django.core import mail
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.base import BaseEmailBackend
from mock import patch

from django_dramatiq_email import tasks
from django_dramatiq_email.utils import dict_to_email, email_to_dict


class TracingBackend(BaseEmailBackend):
    def __init__(self, **kwargs):
        self.__class__.kwargs = kwargs

    def send_messages(self, messages):
        self.__class__.called = True


def check_json_of_msg(msg):
    serialized = json.dumps(email_to_dict(msg))
    assert email_to_dict(dict_to_email(json.loads(serialized))) == email_to_dict(msg)


def test_email_with_attachment():
    file_path = os.path.join(os.path.dirname(__file__), "image.png")
    with open(file_path, "rb") as file:
        file_contents = file.read()
    msg = mail.EmailMessage(
        "test", "Testing with Celery! w00t!!", "from@example.com", ["to@example.com"]
    )
    msg.attach("image.png", file_contents)
    check_json_of_msg(msg)


def test_email_with_mime_attachment():
    file_path = os.path.join(os.path.dirname(__file__), "image.png")
    with open(file_path, "rb") as file:
        file_contents = file.read()
    mimg = MIMEImage(file_contents)
    msg = mail.EmailMessage(
        "test", "Testing with Celery! w00t!!", "from@example.com", ["to@example.com"]
    )
    msg.attach(mimg)
    check_json_of_msg(msg)


def test_email_with_attachment_from_file():
    file_path = os.path.join(os.path.dirname(__file__), "image.png")
    msg = mail.EmailMessage(
        "test", "Testing with Celery! w00t!!", "from@example.com", ["to@example.com"]
    )
    msg.attach_file(file_path)
    check_json_of_msg(msg)


def test_send_single_email_object():
    """It should accept and send a single EmailMessage object."""
    msg = mail.EmailMessage()
    tasks.send_email(msg)
    assert len(mail.outbox) == 1
    assert email_to_dict(msg) == email_to_dict(mail.outbox[0])


def test_send_single_email_object_no_backend_kwargs():
    """It should send email with backend_kwargs not provided."""
    msg = mail.EmailMessage()
    tasks.send_email(msg)
    assert len(mail.outbox) == 1
    assert email_to_dict(msg) == email_to_dict(mail.outbox[0])


def test_send_single_email_dict():
    """It should accept and send a single EmailMessage dict."""
    msg = mail.EmailMessage()
    tasks.send_email(email_to_dict(msg))
    assert len(mail.outbox) == 1
    assert email_to_dict(msg) == email_to_dict(mail.outbox[0])


def test_uses_correct_backend(settings, stub_broker, stub_worker):
    settings.DRAMATIQ_EMAIL_BACKEND = "tests.tests.TracingBackend"
    TracingBackend.called = False
    msg = mail.EmailMessage()
    tasks.send_email.send(email_to_dict(msg))
    stub_broker.join("django_email")
    stub_worker.join()
    assert TracingBackend.called is True


def test_backend_parameters(stub_broker, stub_worker):
    """Our backend should pass kwargs to the 'send_emails' task."""
    with patch("django_dramatiq_email.tasks.get_connection") as mock_connection:
        kwargs = {"auth_user": "user", "auth_password": "pass"}
        mail.send_mass_mail(
            [
                (
                    "test1",
                    "Testing with Celery! w00t!!",
                    "from@example.com",
                    ["to@example.com"],
                ),
                (
                    "test2",
                    "Testing with Celery! w00t!!",
                    "from@example.com",
                    ["to@example.com"],
                ),
            ],
            **kwargs,
        )
        stub_broker.join("django_email")
        stub_worker.join()

    assert mock_connection.call_count == 2
    assert mock_connection.call_args_list[0][1] == {
        "backend": "django.core.mail.backends.locmem.EmailBackend",
        "username": "user",
        "password": "pass",
    }
    assert mock_connection.call_args_list[1][1] == {
        "backend": "django.core.mail.backends.locmem.EmailBackend",
        "username": "user",
        "password": "pass",
    }


def test_failing_connection(stub_broker, stub_worker):
    class Connection:
        def open(self):
            raise Exception("error!")

    with patch(
        "django_dramatiq_email.tasks.get_connection", return_value=Connection()
    ) as mock_connection:
        mail.send_mail(
            "test",
            "Testing with Celery! w00t!!",
            "from@example.com",
            ["to@example.com"],
        )
        stub_broker.join("django_email")
        stub_worker.join()

    # Tried twice, failed to send a mail
    assert mock_connection.call_count == 2
    assert len(mail.outbox) == 0


def test_failing_sending(stub_broker, stub_worker):
    class Connection:
        def open(self):
            pass

        def send_message(self, *args, **kwargs):
            raise Exception("error!")

    with patch(
        "django_dramatiq_email.tasks.get_connection", return_value=Connection()
    ) as mock_connection:
        mail.send_mail(
            "test",
            "Testing with Celery! w00t!!",
            "from@example.com",
            ["to@example.com"],
        )
        stub_broker.join("django_email")
        stub_worker.join()

    # Tried twice, failed to send a mail
    assert mock_connection.call_count == 2
    assert len(mail.outbox) == 0


def test_sending_email(stub_broker, stub_worker):
    tasks = mail.send_mail(
        "test", "Testing with Celery! w00t!!", "from@example.com", ["to@example.com"]
    )
    stub_broker.join("django_email")
    stub_worker.join()
    assert tasks == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "test"


@pytest.mark.parametrize("mixed_subtype", ["mixed", "related"])
def test_sending_html_email(stub_broker, stub_worker, mixed_subtype):
    msg = EmailMultiAlternatives(
        "test", "Testing with Celery! w00t!!", "from@example.com", ["to@example.com"]
    )
    html = "<p>Testing with Celery! w00t!!</p>"
    msg.attach_alternative(html, "text/html")
    msg.mixed_subtype = mixed_subtype
    tasks = msg.send()
    stub_broker.join("django_email")
    stub_worker.join()

    assert tasks == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "test"
    assert len(mail.outbox[0].alternatives) == 1
    assert list(mail.outbox[0].alternatives[0]) == [html, "text/html"]


def test_sending_mail_with_text_attachment(stub_broker, stub_worker):
    msg = mail.EmailMessage(
        "test", "Testing with Celery! w00t!!", "from@example.com", ["to@example.com"]
    )
    msg.attach("image.png", "csv content", "text/csv")
    tasks = msg.send()
    stub_broker.join("django_email")
    stub_worker.join()

    assert tasks == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "test"
    assert mail.outbox[0].content_subtype == "plain"


def test_sending_html_only_email(stub_broker, stub_worker):
    msg = mail.EmailMessage(
        "test",
        "Testing <b>with Celery! w00t!!</b>",
        "from@example.com",
        ["to@example.com"],
    )
    msg.content_subtype = "html"
    tasks = msg.send()
    stub_broker.join("django_email")
    stub_worker.join()

    assert tasks == 1
    assert len(mail.outbox) == 1
    assert mail.outbox[0].subject == "test"
    assert mail.outbox[0].content_subtype == "html"


def test_sending_mass_email(stub_broker, stub_worker):
    emails = (
        ("mass 1", "mass message 1", "from@example.com", ["to@example.com"]),
        ("mass 2", "mass message 2", "from@example.com", ["to@example.com"]),
    )
    tasks = mail.send_mass_mail(emails)
    stub_broker.join("django_email")
    stub_worker.join()

    assert tasks == 2
    assert len(mail.outbox) == 2
    assert {mail.outbox[i].subject for i in range(2)} == {"mass 1", "mass 2"}
