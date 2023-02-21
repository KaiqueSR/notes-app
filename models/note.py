from db import db


class NoteModel(db.Model):
    __tablename__ = "notes"

    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String, nullable=True)
    user_id = db.Column(db.String, db.ForeignKey("users.id"), nullable=False)

    user = db.relationship("UserModel", back_populates="notes")
