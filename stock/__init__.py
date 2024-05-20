"""
Module name: Stock
Authors: IMS Promo Dev Team <imspromo@yncrea.fr>
"""
__version__ = "1.0.0"
import os
from flask import Flask, g, current_app
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_cors import CORS

def create_app() -> Flask:
    db = SQLAlchemy()
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('config.py', silent=False)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
    CORS(app)
    db.init_app(app)
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    with app.app_context():  
        from . import database
        database.init_db(db)
        from . import routes  # Import routes after app is created
    
    return app


app = create_app()

if __name__ == "__main__":
    app.run()