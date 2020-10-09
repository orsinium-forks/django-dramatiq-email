# Django Dramatiq Email

Email backend for Django sending emails via Dramatiq.

[![Test Status](https://github.com/SendCloud/django-dramatiq-email/workflows/Test/badge.svg?branch=master)](https://github.com/SendCloud/django-dramatiq-email/actions?query=workflow%3ATest)
[![Lint Status](https://github.com/SendCloud/django-dramatiq-email/workflows/Lint/badge.svg?branch=master)](https://github.com/SendCloud/django-dramatiq-email/actions?query=workflow%3ALint)
[![Code coverage Status](https://codecov.io/gh/SendCloud/django-dramatiq-email/branch/master/graph/badge.svg)](https://codecov.io/gh/SendCloud/django-dramatiq-email)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

## Installation

To enable `django-dramatiq-email` configure the Django `EMAIL_BACKEND` to `django_dramatiq_email.backends.DramatiqEmailBackend`
and make sure add Django Dramatiq Email to your Django `INSTALLED_APPS`. This package is tested up to Django 3.

## Configuration

The dramatiq task's configuration can be changed via the setting `DRAMATIQ_EMAIL_TASK_CONFIG` of type dict.
By default tasks are being pushed to the 'django_email' queue. The settings in `DRAMATIQ_EMAIL_TASK_CONFIG`
are being used at load time to construct the actor.

Example configuration (using the Retry middleware):
```
DRAMATIQ_EMAIL_TASK_CONFIG = {
    "max_retries": 20,
    "min_backoff": 15000,
    "max_backoff": 86400000,
    "queue_name": "my_custom_queue"
}
```

You can change the actual email backend being used by changing `DRAMATIQ_EMAIL_BACKEND`.

## Bulk emails
Bulk emails are send using individual Dramatiq tasks. Doing so these tasks can be restarted individually.

## Maintainer
[Tim Drijvers](http://github.com/timdrijvers)
