import dramatiq
import pytest
from dramatiq import Worker


@pytest.fixture(scope="function", autouse=True)
def mail_backend(settings):
    settings.EMAIL_BACKEND = "django_dramatiq_email.backends.DramatiqEmailBackend"
    return None


@pytest.fixture(scope="session")
def stub_broker():
    return dramatiq.get_broker()


@pytest.fixture()
def stub_worker(stub_broker):
    worker = Worker(stub_broker, worker_timeout=100, worker_threads=32)
    worker.start()
    yield worker
    worker.stop()
