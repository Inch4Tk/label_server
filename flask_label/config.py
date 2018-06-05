import logging
import sys
from datetime import timedelta

class Config(object):
    """Base Configurations."""
    DEBUG = False
    TESTING = False
    SECRET_KEY = "dev"

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


class Testing(Config):
    """Test Configurations."""
    TESTING = True
    IMAGE_DIR = "images_test"
    VIDEO_DIR = "videos_test"
