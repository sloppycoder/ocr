import logging

from django_tables2 import SingleTableView, tables

from .models import Statement

logger = logging.getLogger(__name__)


class StatementTable(tables.Table):
    class Meta:
        model = Statement
        # template_name = ("django_tables2/bootstrap5.html",)
        fields = ("name", "mime_type", "content_sha", "submitted_at")


class StatementListView(SingleTableView):
    model = Statement
    table_class = StatementTable
    template_name = "statement_list.html"
