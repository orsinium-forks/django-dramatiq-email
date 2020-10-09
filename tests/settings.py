from dramatiq.middleware import TimeLimit

DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": ":memory:"}}


INSTALLED_APPS = (
    "django_dramatiq",
    "django_dramatiq_email",
)


DRAMATIQ_BROKER = {
    "BROKER": "dramatiq.brokers.stub.StubBroker",
    "OPTIONS": {},
    "MIDDLEWARE": [
        "dramatiq.middleware.AgeLimit",
        TimeLimit(time_limit=36000000),
        "dramatiq.middleware.Retries",
    ],
}

SECRET_KEY = "bada bing bada boom"

# Django 1.7 throws dire warnings if this is not set.
# We don't actually use any middleware, given that there are no views.
MIDDLEWARE_CLASSES = ()

EMAIL_BACKEND = "django_dramatiq_email.backends.DramatiqEmailBackend"

DRAMATIQ_EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
DRAMATIQ_EMAIL_TASK_CONFIG = {
    "max_retries": 1,
    "min_backoff": 0,
    "max_backoff": 0,
}
