import functools

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.exceptions import abort

from .models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")

@bp.route("/register", methods=("GET", "POST"))
def register():
    """Handle user registration logic."""
    abort(404)
    # if request.method == "POST":
    #     username = request.form["username"]
    #     password = request.form["password"]
    #     db = get_db()
    #     error = None

    #     if not username:
    #         error = "Username is required."
    #     elif not password:
    #         error = "Password is required."
    #     elif db.execute(
    #         "SELECT id FROM user WHERE username = ?", (username,)
    #     ).fetchone() is not None:
    #         error = "User {} is already registered.".format(username)

    #     if error is None:
    #         db.execute(
    #             "INSERT INTO user (username, password) VALUES (?, ?)",
    #             (username, generate_password_hash(password))
    #         )
    #         db.commit()
    #         return redirect(url_for("auth.login"))

    #     flash(error)

    # return render_template("auth/register.html")

@bp.route("/login", methods=("GET", "POST"))
def login():
    """Handle login logic."""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        error = None
        user = User.query.filter_by(username=username).first()

        if user is None:
            error = "Incorrect username."
        elif not check_password_hash(user.password, password):
            error = "Incorrect password."

        if error is None:
            session.clear()
            session["user_id"] = user.id
            current_app.logger.info('%s logged in successfully', username)
            return redirect(url_for("index"))
        else:
            current_app.logger.info('%s failed to log in', username)

        flash(error)

    return render_template("auth/login.html")

@bp.before_app_request
def load_logged_in_user():
    """Load user information at beginning of each request, to make it available to other views."""
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = User.query.filter_by(id=user_id).first()

@bp.route("/logout")
def logout():
    """Logout logic."""
    session.clear()
    return redirect(url_for("index"))


def login_required(view):
    """Function wrapper for other views. Use with decorator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view

def api_login_required(view):
    """Function wrapper for other views. Use with decorator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return abort(401)

        return view(**kwargs)

    return wrapped_view