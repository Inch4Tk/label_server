import sqlite3

import os
import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash

def init_db():
    """Initialize the Database with tables, users and uses files from instance for labels."""

    db = get_db()
    with current_app.open_resource("schema.sql") as f:
        db.executescript(f.read().decode("utf8"))

    # Setup our userbase
    users = [
        ("test", "test")
    ]
    for user in users:
        db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (user[0], generate_password_hash(user[1]))
        )
    db.commit()

    # Load all files from the images/videos instance folders and save them to db
    init_db_imgfiles(db)
    init_db_videofiles(db)


def init_db_imgfiles(db):
    """Initialize database with img files."""
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

        _, _, labels=next(os.walk(label_dirname))
        # Take only those labels that are xml files, stuff them in dict for fast access
        labels_no_fileending = {x.split(".")[0]:True for x in labels \
                               if x.split(".")[1] in current_app.config["VALID_LABEL_FILE_ENDINGS"]}

        # All images
        _, _, files = next(os.walk(os.path.join(image_dir, d)))
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

def init_db_videofiles(db):
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


@click.command("init-db")
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""

    init_db()
    click.echo("Initialized the database.")

def init_app(app):
    """Register with the application instance."""

    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

def get_db():
    """Get the Database.

    Returns:
        db: Database
    """

    if "db" not in g:
        g.db = sqlite3.connect(
            current_app.config["DATABASE"],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e=None):
    """Close the Database."""

    db = g.pop("db", None)
    if db is not None:
        db.close()