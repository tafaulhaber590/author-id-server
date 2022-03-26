"""
    Thomas: This is the main driver program for the application.
    Most of the actual functionality is delegated to the other modules in this package.
    This module is kind of like a conductor that coordinates them all.
"""

import sys
import secrets
import os

from flask import Flask

from .models import db
from .userviews import login_manager, userviews
from .mainviews import mainviews

CONF_DIR = "config/"
KEYFILE = os.path.join(CONF_DIR, "key.txt")
CONFIG = os.path.join(CONF_DIR, "config.json")
DB_PATH = "authorid.db"


# Ensure that there is a viable secret key for the app to use for session encryption
def ensure_secret_key(forApp: Flask, keypath: str) -> None:
    if not os.path.exists(keypath):
        # If there currently is no key file, create one with a new securely generated key
        with open(keypath, "w") as keyfile:
            key = secrets.token_hex()
            keyfile.write(key)
            forApp.secret_key = key
    else:
        # Otherwise, load the existing key
        with open(keypath, "r") as keyfile:
            forApp.secret_key = keyfile.read()


# Initialize the Flask app
def create_app() -> Flask:
    # Create and configure Flask object
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # Initialize database mediator objects
    db.init_app(app)
    login_manager.init_app(app)

    # Incorporate the userviews and mainviews modules
    app.register_blueprint(userviews, url_prefix="/users")
    app.register_blueprint(mainviews)

    return app


if __name__ == "__main__":
    # Pass "debug" flag in bash to reset the database before and after each run
    flag_debug = "debug" in sys.argv
    try:
        app = create_app()
        app.app_context().push()

        if flag_debug:
            db.drop_all()

        os.makedirs(CONF_DIR, exist_ok=True)

        ensure_secret_key(app, KEYFILE)

        db.create_all()
        app.run(debug=flag_debug)
    except:
        if flag_debug:
            db.drop_all()
        
        raise
