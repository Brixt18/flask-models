from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

MODEL = db.Model
COLUMN = db.Column

STRING = db.String
TEXT = db.Text
INTEGER = db.Integer
FLOAT = db.Float
DATETIME = db.DateTime
BOOLEAN = db.Boolean

FK = db.ForeignKey
