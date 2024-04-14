from statements.models import Statement


def test_seed_data(db):
    statements = Statement.objects.all()
    assert len(statements) > 1
