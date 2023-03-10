from db import db


class UserModel(db.Model):
    __tablename__ = "users"

    id = db.Column(db.String, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)

    notes = db.relationship("NoteModel", back_populates="user")
