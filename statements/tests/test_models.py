from statements.models import Statement


def test_seed_data(db):
    statements = Statement.objects.all()
    assert len(statements) > 0
    assert statements[0].name == "test_invoice.bin"
    assert statements[0].api_response is not None
