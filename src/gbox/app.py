import logging

from flask import (
    Flask,
    render_template,
    request,
    redirect,
    url_for,
    flash,
)
from flask_login import LoginManager, login_user, login_required, logout_user
from flask_socketio import SocketIO, emit
from sqlmodel import select
from werkzeug.middleware.proxy_fix import ProxyFix


from .config import Config
from .constants import *
from .database import get_session, init_db
from .downloader import download_song
from .gbox_queue import GBoxQueue, QueueEntry
from .model import User
from .player import VLCPlayer

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

logger = logging.getLogger(__name__)


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
                session.refresh(user)
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
@socketio.on("connect")
def send_initial_queue():
    """Send the current queue to only the client that just connected."""
    gbox_queue: GBoxQueue = app.config["QUEUE"]

    print(gbox_queue.to_view_list())
    emit("queue_update", gbox_queue.to_view_list())


@socketio.on("submit_song")
def submit(data: dict):
    try:
        yt_url = data["url"]
        username = data["username"]

        song = download_song(yt_url, username)
        gbox_queue: GBoxQueue = app.config["QUEUE"]
        gbox_queue.add_song(song)

        emit("queue_update", gbox_queue.to_view_list(), broadcast=True)
        return {"ok": True}
    except Exception as exc:
        logger.exception("Unable to submit song")
        return {"ok": False, "error": str(exc) or "Unable to add that song."}


# admin event handlers
@socketio.on("admin_pause")
def pause_player():
    player: VLCPlayer = app.config["PLAYER"]
    player.pause()


@socketio.on("admin_skip")
def skip_song():
    player: VLCPlayer = app.config["PLAYER"]
    player.next()

    gbox_queue: GBoxQueue = app.config["QUEUE"]
    print(gbox_queue.to_view_list())

    emit("queue_update", gbox_queue.to_view_list(), broadcast=True)


@socketio.on("admin_remove_song")
def clear_queue():
    gbox_queue: GBoxQueue = app.config["QUEUE"]
    gbox_queue.clear_queue()

    print(gbox_queue.to_view_list())
    emit("queue_update", gbox_queue.to_view_list(), broadcast=True)


@socketio.on("admin_remove_song")
def remove_song(data: dict):
    gbox_queue: GBoxQueue = app.config["QUEUE"]
    gbox_queue.remove_song(QueueEntry(**data["song"]))

    print(gbox_queue.to_view_list())
    emit("queue_update", gbox_queue.to_view_list(), broadcast=True)


@socketio.on("admin_bump_up_song")
def bump_song_up(data: dict):
    gbox_queue: GBoxQueue = app.config["QUEUE"]
    gbox_queue.bump_up(QueueEntry(**data["song"]))

    print(gbox_queue.to_view_list())
    emit("queue_update", gbox_queue.to_view_list(), broadcast=True)


@socketio.on("admin_bump_down_song")
def bump_song_down(data: dict):
    gbox_queue: GBoxQueue = app.config["QUEUE"]
    gbox_queue.bump_down(QueueEntry(**data["song"]))

    print(gbox_queue.to_view_list())
    emit("queue_update", gbox_queue.to_view_list(), broadcast=True)


if __name__ == "__main__":
    init_db()
    app.config["PLAYER"].start()
    socketio.run(
        app,
        host="0.0.0.0",
        port=PORT,
        debug=app.config["DEBUG"],
        use_reloader=app.config["DEBUG"],
    )
