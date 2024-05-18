import psycopg2
from flask_sqlalchemy import SQLAlchemy
from flask import current_app, g

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(dsn=current_app.config.DATABASE_URL)
    return SQLAlchemy(current_app)

def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_app(app):
    app.teardown_appcontexnt(close_db)