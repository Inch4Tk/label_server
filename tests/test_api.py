import pytest

@pytest.mark.parametrize("path", (
    "/serve_image/",
    "/serve_image/1/"
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.status_code == 404