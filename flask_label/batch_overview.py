from flask import (
    Blueprint, current_app, g, redirect, render_template, request, session, url_for
)
from flask_label.auth import login_required
from flask_label.database import db

bp = Blueprint("batch_overview", __name__)

@bp.route("/")
@login_required
def index():
    """List all image and video directories and their stats.
    Allow people to choose one to continue labeling"""
    img_batches = db.execute(
        "SELECT b.id, b.dirname, "
        "COUNT(*) AS img_count, SUM(it.is_labeled) AS labeled_count "
        "FROM image_batch b "
        "INNER JOIN image_task it ON b.id = it.batch_id "
        "GROUP BY b.id "
    ).fetchall()

    video_batches = db.execute(
        "SELECT b.id, b.dirname FROM video_batch b"
    ).fetchall()

    return render_template("batch_overview/index.html",
                           img_batches=img_batches, video_batches=video_batches)