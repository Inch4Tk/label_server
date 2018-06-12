from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from flask_label.auth import login_required
from flask_label.database import db

bp = Blueprint("label_images", __name__,
                url_prefix="/label_images", template_folder="templates/label_images/")

@bp.route("/<int:batch_id>/")
@login_required
def label_batch_overview(batch_id):
    """Give overview of the whole labeling batch. Allow to see and change settings."""
    img_batch = db.execute(
        "SELECT b.id, b.dirname, "
        "COUNT(*) AS img_count, SUM(it.is_labeled) AS labeled_count "
        "FROM image_batch b "
        "INNER JOIN image_task it ON b.id = it.batch_id "
        "WHERE b.id = ? "
        "GROUP BY b.id ",
        (batch_id,)
    ).fetchone()

    img_tasks = db.execute(
        "SELECT it.id, it.filename, it.is_labeled "
        "FROM image_task it "
        "WHERE it.batch_id = ? ",
        (batch_id,)
    ).fetchall()

    return render_template("label_batch_overview.html", img_batch=img_batch, img_tasks=img_tasks)

@bp.route("/<int:batch_id>/<int:task_id>/")
@login_required
def label_task(batch_id, task_id):
    """Present labeling interface."""
    img_task = db.execute(
        "SELECT it.id, it.filename, it.is_labeled "
        "FROM image_task it "
        "WHERE it.id = ? ",
        (task_id,)
    ).fetchone()

    return render_template("label_interface.html", batch_id=batch_id, img_task=img_task)

@bp.route("/<int:batch_id>/next/")
@login_required
def next_task(batch_id):
    """Get a random task from the database, that is not labeled"""
    task_id = db.execute(
        "SELECT it.id "
        "FROM image_task it "
        "WHERE it.batch_id = ? AND it.is_labeled = 0 "
        "ORDER BY RANDOM() "
        "LIMIT 1",
        (batch_id,)
    ).fetchone()
    if task_id is None:
        return "Could not find any more unlabeled examples." # TODO Make Correct error page

    return redirect(url_for("label_images.label_task",
                            batch_id=batch_id, task_id=task_id["id"]), code=303)

