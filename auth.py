
import functools
import bcrypt
import os
from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, current_app
)
from forms import RegistrationForm, LoginForm

bp = Blueprint("auth", __name__, url_prefix="/auth")

def get_db():
    return current_app.db

@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        try:
            hashed_password = bcrypt.hashpw(form.password.data.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            user = get_db().add_with_validation(
                "Users",
                {
                    "name": form.name.data,
                    "email": form.email.data,
                    "contact_number": form.contact_number.data,
                    "nid_number": form.nid_number.data,
                    "password_hash": hashed_password,
                    "role": form.role.data,
                    "email_verified": False,
                    "nid_verified": False,
                    "status": "active",
                },
                unique_fields=["email", "nid_number"],
            )
            flash("Registration successful! Please log in.", "success")
            return redirect(url_for("auth.login"))
        except ValueError as e:
            flash(str(e), "error")

    return render_template("auth/register.html", form=form)

@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        users = get_db().find_by_attribute("Users", "email", form.email.data)
        user = users[0] if users else None

        if user is None:
            flash("Incorrect email.", "error")
        elif not bcrypt.checkpw(form.password.data.encode("utf-8"), user["password_hash"].encode("utf-8")):
            flash("Incorrect password.", "error")
        else:
            session.clear()
            session["user_id"] = user["id"]
            flash("Logged in successfully!", "success")
            return redirect(url_for("index"))

    return render_template("auth/login.html", form=form)

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().get_by_id("Users", user_id)

@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for("auth.login"))

        return view(**kwargs)

    return wrapped_view


