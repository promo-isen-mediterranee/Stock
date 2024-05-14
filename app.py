from flask import Flask, make_response, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = \
    "postgresql://postgres:postgres@localhost:5432/logistisen_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app)
db = SQLAlchemy(app)