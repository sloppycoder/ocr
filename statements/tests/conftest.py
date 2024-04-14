import os
import sys

import pytest
from django.core.management import call_command

from statements.models import Statement

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
    Statement.objects.bulk_create(
        [
            Statement(name="doument_1.pdf", mime_type="application.pdf"),
            Statement(name="statement_2.pdf", mime_type="application.pdf"),
        ]
    )
