from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
    session,
    jsonify,
)
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_socketio import SocketIO, emit
from sqlmodel import select
from werkzeug.middleware.proxy_fix import ProxyFix

from .constants import *
from .database import get_session
from .downloader import download_song
from .model import User, Config
from .queue import GBoxQueue

app = Flask(__name__)
app.config.from_object(Config)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

socketio = SocketIO(
    app,
    cors_allowed_origins=app.config["CORS_ORIGINS"],
    logger=True,
    engineio_logger=True,
)


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
            login_user(user)
            flash(f"Welcome {user.username}!")
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
@socketio.on("submit_song")
def submit(data: dict):
    try:
        yt_url = data["url"]
        username = data["username"]

        song = download_song(yt_url, username)
        gbox_queue = app.config["QUEUE"]
        gbox_queue.add_song(song)

        emit("song_added", gbox_queue.to_json(), broadcast=True)
    except:
        pass


# ADMIN EVENT HANDLERS

# TODO: Add an event handler for pause/play

# TODO: Add an event handler for skip

# TODO: Add an event handler for deleting/removing a song

# TODO: Add an event handler for bump song up

# TODO: Add an event handler for bump song down


if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=PORT,
        debug=app.config["DEBUG"],
        use_reloader=app.config["DEBUG"],
    )
