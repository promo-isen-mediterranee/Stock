"""
Module name: Stock
Authors: IMS Promo Dev Team <imspromo@yncrea.fr>
"""
__version__ = "1.0.0"
import os
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

def create_app(test_config=None):
    """
    Create and configure the Flask application.

    Args:
        test_config (dict, optional): A dictionary of configuration settings for testing. Defaults to None.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=True)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    CORS(app)
    db = SQLAlchemy(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

