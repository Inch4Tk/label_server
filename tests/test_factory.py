from flask_label import create_app
import flask_label.config

def test_config():
    assert not create_app().testing
    assert create_app(flask_label.config.Testing()).testing
