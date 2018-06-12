import os

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app, send_from_directory
)
from flask_label.auth import api_login_required
from flask_label.database import db

bp = Blueprint("api", __name__,
                url_prefix="/api")

@bp.route("/batch/<int:img_id>/")
@api_login_required
def get_batch():
    pass

@bp.route("/serve_image/<int:img_id>/")
@api_login_required
def serve_image(img_id):
    """Serves an image from the instance folder

    Args:
        img_id (int): Is the same as task id, since every task is matched to one image.
    """
    img_tasks = db.execute(
        "SELECT it.filename, b.dirname "
        "FROM image_task it "
        "INNER JOIN image_batch b ON b.id = it.batch_id "
        "WHERE it.id = ? ",
        (img_id,)
    ).fetchone()

    img_path = os.path.join(
        current_app.instance_path,
        current_app.config["IMAGE_DIR"],
        img_tasks["dirname"]
    )

    current_app.logger.info(os.path.join(img_path, img_tasks["filename"]))
    return send_from_directory(img_path, img_tasks["filename"])