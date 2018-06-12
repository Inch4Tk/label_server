import logging
import sys
import os
from datetime import timedelta

class Config(object):
    """Base Configurations."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = "dev"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directories for labeling
    VALID_IMG_FILE_ENDINGS = ["png", "jpg", "jpeg"]
    VALID_LABEL_FILE_ENDINGS = ["xml"]
    IMAGE_DIR = "images"
    IMAGE_LABEL_SUBDIR = "labels"
    VIDEO_DIR = "videos"
    VIDEO_IMG_SUBDIR = "images"
    VIDEO_LABEL_SUBDIR = "labels"


class Dev(Config):
    """Development Configurations."""
    DEBUG = True

    def __init__(self, instance_path):
        self.DBNAME = "flask_label.sqlite"
        self.DATABASE = os.path.join(instance_path, self.DBNAME)
        self.SQLALCHEMY_DATABASE_URI = "sqlite:////{}".format(self.DATABASE)
        super().__init__()

class Testing(Config):
    """Test Configurations."""
    TESTING = True
    IMAGE_DIR = "images_test"
    VIDEO_DIR = "videos_test"

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    DATABASE = "test"
    SQLALCHEMY_DATABASE_URI = "test"

class Mock(Config):
    """Mock configuration for tests."""
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DATABASE = "test"
    SQLALCHEMY_DATABASE_URI = "test"