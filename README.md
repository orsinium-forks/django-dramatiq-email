# Django Dramatiq Email

Email backend for Django sending emails via Dramatiq.

This package is tested up to Django 4.1.

[![Test Status](https://github.com/SendCloud/django-dramatiq-email/workflows/Test/badge.svg?branch=master)](https://github.com/SendCloud/django-dramatiq-email/actions?query=workflow%3ATest)
[![Lint Status](https://github.com/SendCloud/django-dramatiq-email/workflows/Lint/badge.svg?branch=master)](https://github.com/SendCloud/django-dramatiq-email/actions?query=workflow%3ALint)
[![Code coverage Status](https://codecov.io/gh/SendCloud/django-dramatiq-email/branch/master/graph/badge.svg)](https://codecov.io/gh/SendCloud/django-dramatiq-email)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Installation

To enable `django-dramatiq-email`, modify your project `settings.py`:

- Add `"django_dramatiq_email"` to `INSTALLED_APPS` below `"django_dramatiq"`,
- Set `EMAIL_BACKEND` to `"django_dramatiq_email.backends.DramatiqEmailBackend"`,
- Set `DRAMATIQ_EMAIL_BACKEND` to the actual email backend you want to use (SMTP, Anymail, etc),
- Optionally, add the `DRAMATIQ_EMAIL_TASK_CONFIG` dict as shown below.

## Configuration

The `dramatiq.actor` args ([reference](https://dramatiq.io/reference.html#dramatiq.actor), [user guide](https://dramatiq.io/guide.html)) for `send_email` can be set via the `DRAMATIQ_EMAIL_TASK_CONFIG` dict in your `settings.py`.

The default args are [here](django_dramatiq_email/tasks.py) - most notably, the default `queue_name` is `django_email`.

Example configuration (using the Retry middleware):

```python
DRAMATIQ_EMAIL_TASK_CONFIG = {
    "max_retries": 20,
    "min_backoff": 15000,
    "max_backoff": 86400000,
    "queue_name": "my_custom_queue"
}
```

## Bulk emails
Bulk emails are send using individual Dramatiq tasks. Doing so these tasks can be restarted individually.

## Maintainer
[Tim Drijvers](http://github.com/timdrijvers)
