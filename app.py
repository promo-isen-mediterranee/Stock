from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
<<<<<<< HEAD
from dotenv import load_dotenv
import os

load_dotenv('.flaskenv')
=======
from werkzeug.middleware.proxy_fix import ProxyFix
>>>>>>> cb64b2ea5ed9e5416bf64b33bc02d2ea4ae45cad

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
CORS(app)
db = SQLAlchemy(app)