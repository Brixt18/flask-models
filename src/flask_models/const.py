from flask_sqlalchemy import SQLAlchemy

# from app import db

db = None

def configurate_db(sqlachemy_db:SQLAlchemy):
    db = sqlachemy_db

MODEL = db.Model
COLUMN = db.Column

STRING = db.String
TEXT = db.Text
INTEGER = db.Integer
FLOAT = db.Float
DATETIME = db.DateTime
BOOLEAN = db.Boolean

FK = db.ForeignKey
