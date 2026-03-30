import pytest
import requests

pytest.register_assert_rewrite("tests.utils.models")


@pytest.fixture(scope="session")
def session():
    session = requests.session()
    return session


@pytest.fixture
def payment(session):
    from .utils.models import Payment as PaymentModel

    return PaymentModel(session)
