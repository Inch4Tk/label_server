from flask import (
    Blueprint, current_app, g, redirect, render_template, request, session, url_for
)
from flask_label.auth import login_required
from flask_label.models import ImageBatch, VideoBatch

bp = Blueprint("batch_overview", __name__)

@bp.route("/")
@login_required
def index():
    """List all image and video directories and their stats.
    Allow people to choose one to continue labeling"""
    img_batches = ImageBatch.query.all()
    # img_batches.tasks
    for batch in img_batches:
        batch.img_count = len(batch.tasks)
        lc = 0
        for task in batch.tasks:
            if task.is_labeled:
                lc += 1
        batch.labeled_count = lc

    # db.execute(
    #     "SELECT b.id, b.dirname, "
    #     "COUNT(*) AS img_count, SUM(it.is_labeled) AS labeled_count "
    #     "FROM image_batch b "
    #     "INNER JOIN image_task it ON b.id = it.batch_id "
    #     "GROUP BY b.id "
    # )

    video_batches = VideoBatch.query.all()

    return render_template("batch_overview/index.html",
                           img_batches=img_batches, video_batches=video_batches)