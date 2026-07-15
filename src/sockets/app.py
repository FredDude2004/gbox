import json
import re

from flask import Flask, render_template
from flask_socketio import SocketIO, emit

from collections import deque
from dataclasses import dataclass

from constants import yt_id_regex, yt_url_regex

app = Flask(__name__)
app.config["SECRET_KEY"] = "dev-secret"

socketio = SocketIO(app, cors_allowed_origins="*")
