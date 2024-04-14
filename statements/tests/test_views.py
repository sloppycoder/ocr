from statements.urls import app_name


def test_list_view(client, db):
    response = client.get(f"/{app_name}", follow=True)
    assert response.status_code == 200
    assert bytes("List of Statements", "utf-8") in response.content


def test_upload_view(client, db):
    response = client.get(f"/{app_name}/upload", follow=True)
    assert response.status_code == 200
    assert bytes("Upload", "utf-8") in response.content
