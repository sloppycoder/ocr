import os

from django.core.files.uploadedfile import SimpleUploadedFile

from statements.models import Statement
from statements.urls import app_name

test_data_dir = os.path.join(os.path.dirname(__file__), "data")


def test_list_view(client, db):
    response = client.get(f"/{app_name}", follow=True)
    assert response.status_code == 200
    assert bytes("List of Statements", "utf-8") in response.content
    assert bytes("test_invoice", "utf-8") in response.content


def test_statement_upload_view(client, db):
    response = client.get(f"/{app_name}/upload", follow=True)
    assert response.status_code == 200
    assert bytes("Upload", "utf-8") in response.content


def test_statement_upload(client, db):
    with open(f"{test_data_dir}/test_invoice.bin", "rb") as f:
        response = client.post(
            f"/{app_name}/upload",
            {
                "name": "unit_test.pdf",
                "uploaded_file": SimpleUploadedFile("unit_test.pdf", f.read()),
            },
        )
        # the upload page redirects to list page upon successful upload
        assert response.status_code == 302

        new_statement = Statement.objects.filter(name="unit_test.pdf").first()
        # the uploaded statement matches an existing ApiResponse
        assert new_statement.content_sha == new_statement.api_response.content_sha
