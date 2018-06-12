import os
import click
from flask.cli import with_appcontext

from .database import db
from .models import User, ImageTask, ImageBatch, VideoBatch

def db_drop_all():
    """Drops all tables."""
    db.drop_all()

def db_init_users():
    """Initialize the Database with tables, users and uses files from instance for labels."""

    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if table == "user":
            session.execute(table.delete())

    test_user = User(username="test", password="pbkdf2:sha256:50000$be1GSrVN$138ec4c121339bc34d64527f6210ac1e6e8eab6792662e95532382db7ece2adf")
    db.session.add(test_user)
    db.session.commit()


def db_update_task():
    """Updates the database for batches and labeling tasks, based on the instance folder."""

    # Clear stuff from database
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        if table == "image_task" or table == "image_batch" or table == "video_batch":
            session.execute(table.delete())

    # Load all files from the images/videos instance folders and save them to db
    db_init_imgfiles(db)
    db_init_videofiles(db)


def db_init_imgfiles(db):
    """Initialize database with img files.

    The idea is to look for all subdirs of the image folder, which is in the instance folder.
    Then add one label batch entry to the database for every folder.
    Then fetch all the labels from the labels subfolder. Add those labels to the database.
    Then fetch all image files. Add them to the db, set values depending on if they are or not labeled.

    Labels need to have the same name as images. (except fileending)
    The folder names are configured in instance/config.py.
    Defaults are defined in label_server/config.py.

    """
    image_dir = os.path.join(current_app.instance_path, current_app.config["IMAGE_DIR"])
    if not os.path.isdir(image_dir):
        os.makedirs(image_dir)

    _, subdirs, _ = next(os.walk(image_dir))
    db_cur = db.cursor()
    for d in subdirs:
        db_cur.execute(
            "INSERT INTO image_batch (dirname) VALUES (?)",
            (d, )
        )
        batch_id = db_cur.lastrowid

        # ALl labels
        label_dirname = os.path.join(image_dir, d, current_app.config["IMAGE_LABEL_SUBDIR"])
        if not os.path.isdir(label_dirname):
            os.makedirs(label_dirname)

        _, _, labels = next(os.walk(label_dirname))
        # Take only those labels that are xml files, stuff them in dict for fast access
        labels_no_fileending = {x.split(".")[0]:True for x in labels \
                               if x.split(".")[1] in current_app.config["VALID_LABEL_FILE_ENDINGS"]}

        # All images
        _, _, files = next(os.walk(os.path.join(image_dir, d)))
        files.sort()
        for f in files:
            splits = f.split(".")
            f_no_fileending = splits[0]
            f_file_ending = splits[1]
            # Sort out everything that is not an image
            if f_file_ending not in current_app.config["VALID_IMG_FILE_ENDINGS"]:
                continue
            is_labeled = False

            # Check if we have a label
            if f_no_fileending in labels_no_fileending:
                is_labeled = True
            # Insert the image + label into db
            db_cur.execute(
                "INSERT INTO image_task (filename, is_labeled, batch_id) VALUES (?, ?, ?)",
                (f, is_labeled, batch_id)
            )

        db.commit()

def db_init_videofiles(db):
    """Initialize database with videofiles."""
    video_dir = os.path.join(current_app.instance_path, current_app.config["VIDEO_DIR"])
    if not os.path.isdir(video_dir):
        os.makedirs(video_dir)

    _, subdirs, _ = next(os.walk(video_dir))
    db_cur = db.cursor()
    for d in subdirs:
        db_cur.execute(
            "INSERT INTO video_batch (dirname) VALUES (?)",
            (d, )
        )
        batch_id = db_cur.lastrowid

        db.commit()


@click.command("db-init-user")
@with_appcontext
def db_init_user_command():
    """Clear the existing user data and set users"""
    db_init_users()
    click.echo("Initialized the User database.")

@click.command("db-update-task")
@with_appcontext
def db_update_task_command():
    """Clear existing batches and tasks tables, then fill it based on info in the instance folder."""
    db_update_task()
    click.echo("Updated the batch and tasks in the database.")

@click.command("db-drop-all")
@with_appcontext
def db_drop_all_command():
    """Clear everything"""
    db_drop_all()
    click.echo("Cleared the whole db.")

def init_db_cli(app):
    """Register with the application instance."""
    app.cli.add_command(db_init_user_command)
    app.cli.add_command(db_update_task_command)
    app.cli.add_command(db_drop_all_command)
