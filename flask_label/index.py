from flask import (
    Blueprint, current_app, g, redirect, render_template, request, session, url_for
)
from flask_label.auth import login_required
from flask_label.models import ImageBatch, VideoBatch

bp = Blueprint("index", __name__)

@bp.route("/", defaults={"path": ""})
@bp.route("/<path:path>")
@login_required
def index(path=None):
    """Returns the react Single Page Application."""
    return render_template("index.html")