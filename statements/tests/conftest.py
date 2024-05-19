import hashlib
import os
import sys
from glob import glob

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
        seed_confidential_data()


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


def _seed_statement_data_(statement_file: str, response_file: str):
    with open(statement_file, "rb") as statement_f:
        statement_content = statement_f.read()
        content_sha = hashlib.sha1(statement_content).hexdigest()

        with open(response_file, "rb") as response_f:
            response = ApiResponse.objects.create(
                mime_type="application/pdf",
                content_sha=content_sha,
                response=response_f.read(),
            )

            Statement.objects.create(
                name=os.path.basename(statement_file),
                mime_type="application/pdf",
                content_sha=content_sha,
                content=statement_content,
                api_response=response,
            )


def seed_data():
    test_data_dir = os.path.join(os.path.dirname(__file__), "data")
    _seed_statement_data_(f"{test_data_dir}/test_invoice.bin", f"{test_data_dir}/test_api_response.bin")


def seed_confidential_data():
    data_dir = os.environ.get("STATEMENTS_DIR", os.path.expanduser("~/Documents/hsbc_statements"))
    for statement_file in glob(f"{data_dir}/*.pdf"):
        _seed_statement_data_(statement_file, statement_file.replace(".pdf", "_response.bin"))
