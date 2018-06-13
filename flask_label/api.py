import os

from flask import (
    Blueprint, redirect, current_app, send_from_directory, jsonify
)
from flask_label.auth import api_login_required
from flask_label.database import db
from flask_label.models import (
    ImageTask, ImageBatch, VideoBatch, image_batch_schema, video_batch_schema
)

bp = Blueprint("api", __name__,
                url_prefix="/api")

@bp.route("/batches/")
@api_login_required
def batches():
    """Return all image and video directories and their stats."""
    img_batches = ImageBatch.query.options(db.joinedload('tasks')).all()
    video_batches = VideoBatch.query.all()

    image_batch_data = image_batch_schema.dump(img_batches, many=True).data
    video_batch_data = video_batch_schema.dump(img_batches, many=True).data

    # Add postprocessing info about statistics
    for batch in image_batch_data:
        batch["img_count"] = len(batch["tasks"])
        lc = 0
        for task in batch["tasks"]:
            if task["is_labeled"]:
                lc += 1

        batch["labeled_count"] = lc

    return jsonify({"image_batches": image_batch_data, "video_batches": video_batch_data})


@bp.route("/serve_image/<int:img_id>/")
@api_login_required
def serve_image(img_id):
    """Serves an image from the instance folder

    Args:
        img_id (int): Is the same as task id, since every task is matched to one image.
    """
    img_task = ImageTask.query.filter_by(id=img_id).first()

    img_path = os.path.join(
        current_app.instance_path,
        current_app.config["IMAGE_DIR"],
        img_task.batch.dirname
    )

    current_app.logger.info(os.path.join(img_path, img_task.filename))
    return send_from_directory(img_path, img_task.filename)