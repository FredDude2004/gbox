from flask import Flask, render_template, request, redirect, url_for, flash
from flask_login import LoginManager, login_user, login_required, logout_user

from sqlmodel import select

from .model import User
from .database import get_session
from .constants import *

app = Flask(__name__)
app.secret_key = "KEY_HERE_I_GUESS"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@login_manager.user_loader
def load_user(user_id):
    with next(get_session()) as session:
        statement = select(User).where(User.id == user_id)
        user = session.exec(statement).first()

        return user


@app.route("/")
@login_required
def index():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")

        # Simple hardcoded validation (Replace this with database verification!)
        if username == "admin":
            return redirect(url_for("admin"))
        else:
            with next(get_session()) as session:
                user = User(username=str(username))
                session.add(user)
                session.commit()
            return redirect(url_for("index"))

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        password = request.form.get("password")

        if password == ADMIN_PASSWORD:
            return redirect(url_for("admin-index.html"))
        else:
            flash("Invalid username or password", "error")
            return redirect(url_for("login"))

    return render_template("admin-password.html")


# socket event handlers

# TODO: Add an event handler for when a user submits a url
#       The handler should return the entire state of the queue
#       The frontend should then update the queue on the screen

# ADMIN EVENT HANDLERS

# TODO: Add an event handler for pause/play

# TODO: Add an event handler for skip

# TODO: Add an event handler for bump song up

# TODO: Add an event handler for move song down
