import os

from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from statements.models import Statement
from statements.urls import app_name

test_data_dir = os.path.join(os.path.dirname(__file__), "data")


def test_list_view(auth_client, db):
    response = auth_client.get(reverse(f"{app_name}:index"), follow=True)
    assert response.status_code == 200
    assert bytes("List of Statements", "utf-8") in response.content
    # assert bytes("test_invoice", "utf-8") in response.content


def test_statement_upload_view(auth_client, db):
    response = auth_client.get(reverse(f"{app_name}:upload"))
    assert response.status_code == 200
    assert bytes("Upload", "utf-8") in response.content


def test_statement_upload_success(auth_client, db):
    with open(f"{test_data_dir}/test_invoice.bin", "rb") as f:
        response = auth_client.post(
            reverse(f"{app_name}:upload"),
            {
                "name": "unit_test.pdf",
                "uploaded_file": SimpleUploadedFile("unit_test.pdf", f.read()),
            },
        )
        # the upload page redirects to list page upon successful upload
        assert response.status_code == 302
        messages = list(get_messages(response.wsgi_request))
        assert "uploaded" in messages[0].message

        new_statement = Statement.objects.filter(name="unit_test.pdf").first()
        # the uploaded statement matches an existing ApiResponse
        assert new_statement.content_sha == new_statement.api_response.content_sha


def test_statement_upload_rejected(auth_client, db):
    with open(f"{test_data_dir}/test_invoice.bin", "rb") as f:
        response = auth_client.post(
            reverse(f"{app_name}:upload"),
            {
                "name": "unit_test.bin",
                "uploaded_file": SimpleUploadedFile("unit_test.pdf", f.read()),
            },
        )
        # the upload page will refresh with an error message
        assert response.status_code == 200
        messages = list(get_messages(response.wsgi_request))
        assert "invalid" in messages[0].message


def test_list_view_noauth(client, db):
    response = client.get(reverse(f"{app_name}:index"))
    assert response.status_code == 302
    assert "/accounts/login" in response.headers["Location"]
