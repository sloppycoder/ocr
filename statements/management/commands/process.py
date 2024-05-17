from django.core.management.base import BaseCommand

from statements.parser import extract_from_statements


class Command(BaseCommand):
    requires_migrations_checks = True
    help = "Bulk processing sttements to extract transaction details"  # noqa A003

    def add_arguments(self, parser):
        parser.add_argument("--name", dest="name", required=True, help="Name filter, e.g. 2020_08")

    def handle(self, *_, **options):
        extract_from_statements(options["name"])
