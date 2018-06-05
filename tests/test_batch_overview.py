import pytest
from flask_label.db import get_db


def test_index(client, auth):
    response = client.get("/")
    assert response.headers["Location"] == "http://localhost/auth/login"

    auth.login()
    response = client.get("/")
    assert b"Log Out" in response.data
    assert b"burger_crawled_example" in response.data
    assert b"yt_extract" in response.data
    assert b"Images: 5" in response.data
    assert b"Labels: 5" in response.data
    assert b"Percentage: 100.0" in response.data
    assert b'href="/label_images/1/"' in response.data

