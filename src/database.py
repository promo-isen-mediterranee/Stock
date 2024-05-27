from flask import g

def init_db(db):
    g.db = db

def get_db():
    return g.db