import os
import sys

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client

from statements.models import ApiResponse, Statement

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(f"{cwd}/.."))

_TEST_USERNAME_ = "appuser"
_TEST_PASSWORD_ = "apppass"


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        call_command("migrate", interactive=False)
        seed_data()


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username=_TEST_USERNAME_, password=_TEST_PASSWORD_)


@pytest.fixture
def auth_client(user):
    client = Client()
    authenticated = client.login(username=_TEST_USERNAME_, password=_TEST_PASSWORD_)
    assert authenticated
    return client


@pytest.fixture
def logged_in_client(client, db):
    client.login(username=_TEST_USERNAME_, password=_TEST_PASSWORD_)
    yield client


def seed_data():
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")

    with open(f"{test_data_dir}/test_api_response.bin", "rb") as invoice_f:
        with open(f"{test_data_dir}/test_invoice.bin", "rb") as response_f:
            response = ApiResponse.objects.create(
                mime_type="application/pdf",
                content_sha="58b4ab33560a9f953b8424ad228e0f5016e1ab96",
                response=invoice_f.read(),
            )

            Statement.objects.create(
                name="test_invoice.pdf",
                mime_type="application/pdf",
                content_sha="58b4ab33560a9f953b8424ad228e0f5016e1ab96",
                content=response_f.read(),
                api_response=response,
            )
