# models.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Poem(db.Model):
    __tablename__ = "poems"
    id = db.Column(db.Integer, primary_key=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(255), nullable=False)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
