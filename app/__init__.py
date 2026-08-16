"""
Provided Flask application factory.

You do not need to read or change anything in the `app/` package. It builds the
web interface and calls the methods of ScheduleService. All the logic you write
lives behind ScheduleService, not here.
"""

from __future__ import annotations

import os
from flask import Flask

from schedule_service import ScheduleService

# Path to the provided dataset.
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data",
                         "sessions.csv")


def create_app() -> Flask:
    app = Flask(__name__)
    # Needed so flashed messages work. This is a teaching app, not production,
    # so a fixed development key is fine.
    app.secret_key = "conference-session-planner-dev-key"

    # One ScheduleService for the life of the app. Students' state lives here.
    service = ScheduleService()

    # Try to load the catalogue at startup. If the student has not implemented
    # load_sessions yet, the app still starts; pages will report what is missing.
    try:
        service.load_sessions(DATA_PATH)
        app.config["DATA_LOADED"] = True
    except NotImplementedError:
        app.config["DATA_LOADED"] = False
    except Exception as exc:  # malformed file, etc.
        app.config["DATA_LOADED"] = False
        app.config["LOAD_ERROR"] = str(exc)

    app.config["SERVICE"] = service
    app.config["DATA_PATH"] = DATA_PATH

    from app.routes import bp
    app.register_blueprint(bp)
    return app
