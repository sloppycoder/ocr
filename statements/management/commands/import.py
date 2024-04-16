import glob
import os

from django.core.management.base import BaseCommand

from statements.service import save_file


class Command(BaseCommand):
    requires_migrations_checks = True
    help = "Bulk import sttements"  # noqa A003

    def add_arguments(self, parser):
        parser.add_argument("--source", dest="source", required=True, help="Directory for statements to import")

    def handle(self, *args, **options):
        source_dir = os.path.expanduser(options["source"])
        for file_name in glob.glob(f"{source_dir}/*.pdf"):
            with open(file_name, "rb") as f:
                save_file(
                    file_name=os.path.basename(file_name),
                    mime_type="application/pdf",
                    file_content=f.read(),
                )
                print(f"imported {file_name}")
