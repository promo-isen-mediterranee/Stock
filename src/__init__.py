"""
Module name: Stock
Authors: IMS Promo Dev Team <imspromo@yncrea.fr>
"""
__version__ = "1.0.0"

import signal
import sys
from os import environ, makedirs

from flask import Flask
from flask_cors import CORS
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix


def init_app_config(app: Flask) -> None:
    app.config['SQLALCHEMY_DATABASE_URI'] = \
        f"postgresql://{environ.get('DB_USER')}:{environ.get('DB_PASSWORD')}@{environ.get('DB_HOST')}:{environ.get('DB_PORT')}/{environ.get('DB_NAME')}"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = environ.get('SQLALCHEMY_TRACK_MODIFICATIONS')

    app.secret_key = environ.get('SECRET_KEY')

    app.config["SESSION_COOKIE_HTTPONLY"] = environ.get("SESSION_COOKIE_HTTPONLY")
    app.config["SESSION_COOKIE_SAMESITE"] = environ.get("SESSION_COOKIE_SAMESITE")
    app.config["SESSION_COOKIE_DOMAIN"] = environ.get("SESSION_COOKIE_DOMAIN")



def create_app() -> Flask:
    app = Flask(__name__, instance_relative_config=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

    init_app_config(app)

    db = SQLAlchemy(app)
    CORS(app, supports_credentials=True)
    LoginManager(app)

    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():
        app.db = db
        from . import routes  # Import routes after app is created

    return app


app = create_app()

signal.signal(signal.SIGTERM, lambda x, y: sys.exit(0))


if __name__ == "__main__":
    app.run()
