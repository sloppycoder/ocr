import os
import sys

import pytest
from django.core.management import call_command

from statements.models import ApiResponse, Statement

cwd = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(f"{cwd}/.."))


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):
    """
    a memory database is setup automatically by django,
    the schema is created so no need to run migration
    """
    with django_db_blocker.unblock():
        call_command("migrate", interactive=False)
        seed_data()


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
