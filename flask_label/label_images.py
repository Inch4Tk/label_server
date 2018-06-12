import random

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from flask_label.auth import login_required
from flask_label.models import ImageBatch, ImageTask

bp = Blueprint("label_images", __name__,
                url_prefix="/label_images", template_folder="templates/label_images/")

@bp.route("/<int:batch_id>/")
@login_required
def label_batch_overview(batch_id):
    """Give overview of the whole labeling batch. Allow to see and change settings."""
    img_batch = ImageBatch.query.filter_by(id=batch_id).first()
    img_batch.img_count = len(img_batch.tasks)
    lc = 0
    for task in img_batch.tasks:
        if task.is_labeled:
            lc += 1
    img_batch.labeled_count = lc

    return render_template("label_batch_overview.html", img_batch=img_batch)

@bp.route("/<int:batch_id>/<int:task_id>/")
@login_required
def label_task(batch_id, task_id):
    """Present labeling interface."""
    img_task = ImageTask.query.filter_by(id=task_id).first()

    return render_template("label_interface.html", batch_id=batch_id, img_task=img_task)

@bp.route("/<int:batch_id>/next/")
@login_required
def next_task(batch_id):
    """Get a random task from the database, that is not labeled"""
    img_tasks = ImageTask.query.filter_by(batch_id=batch_id, is_labeled=False).all()

    if not img_tasks:
        return "Could not find any more unlabeled examples." # TODO Make Correct error page

    img_task = random.choice(img_tasks)
    return redirect(url_for("label_images.label_task",
                            batch_id=batch_id, task_id=img_task.id), code=303)

