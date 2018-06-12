import pytest
from flask_label.database import db

@pytest.mark.parametrize("path", (
    "/label_images/1/",
    "/label_images/1/1/",
    "/label_images/1/next/"
))
def test_login_required(client, path):
    response = client.get(path)
    assert response.headers["Location"] == "http://localhost/auth/login"

def test_task_overview(client, auth):
    auth.login()

    response = client.get("/label_images/1/")

    assert b"Images: 5" in response.data
    assert b"Labels: 5" in response.data
    assert b"Percentage: 100.0" in response.data

    assert b"0a5a79b07ac1b11b1f353c792411bc02.png, Labeled: True" in response.data
    assert b"" in response.data

    response = client.get("/label_images/2/")
    assert b"0Q0HfMGgJJU1.png, Labeled: False" in response.data

    assert b'href="/">Back' in response.data
    assert b'href="/label_images/2/next/"' in response.data
    assert b'href="/label_images/2/6/"' in response.data

def test_next_task(client, auth):
    auth.login()
    for _ in range(10):
        response = client.get("/label_images/2/next/")
        target = int(response.headers["Location"].split("/")[-2])

        assert target >= 6 and target <= 8

    response = client.get("/label_images/1/next/")
    assert b"Could not find any more unlabeled examples." in response.data

def test_label_interface(client, auth):
    auth.login()
    response = client.get("/label_images/1/1/")

    assert b"Label Interface" in response.data
    assert b"Label Image 1: 0a5a79b07ac1b11b1f353c792411bc02.png" in response.data
    assert b"Link to image: /api/serve_image/1/" in response.data

    assert b'href="/label_images/1/">Back' in response.data
    assert b'href="/label_images/1/next/"' in response.data