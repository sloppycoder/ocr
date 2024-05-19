import os

from django.core.management.base import BaseCommand

from statements.models import Statement


class Command(BaseCommand):
    requires_migrations_checks = True
    help = "Bulk export API responses"  # noqa A003

    def add_arguments(self, parser):
        parser.add_argument("--dest", dest="dest", required=True, help="Directory to save output")

    def handle(self, *args, **options):
        dest_dir = os.path.expanduser(options["dest"])

        for statement in Statement.objects.all():
            name = statement.name
            if statement.api_response:
                file_name = f"{dest_dir}/{name}".replace(".pdf", "_response.bin")
                with open(file_name, "wb") as f:
                    f.write(statement.api_response.response)
                print(f"Saved {file_name}")
