import os
from glob import glob

import pytest

from statements.models import Statement
from statements.parser import extract_from_statements

test_data_dir = os.environ.get("STATEMENTS_DIR", os.path.expanduser("~/Documents/hsbc_statements"))
n_statement_files = len(glob(f"{test_data_dir}/*.pdf"))


@pytest.mark.skipif(n_statement_files <= 0, reason="confidential data not available")
def test_parser(db):
    extract_from_statements("2020_04")
    transactions = Statement.objects.filter(name="HSBC_VN_2020_04.pdf").first().transactions.all()
    assert len(transactions) > 0
