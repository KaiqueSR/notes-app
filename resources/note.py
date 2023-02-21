from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from uuid import uuid4

from db import db
from models import NoteModel
from schemas import NoteSchema

blp = Blueprint("Notes", "notes", description="Operations on notes")


@blp.route("/notes")
class Notes(MethodView):
    @jwt_required()
    @blp.arguments(NoteSchema)
    @blp.response(201, NoteSchema)
    def post(self, note_data):
        identity = get_jwt_identity()
        id = str(uuid4())
        note = NoteModel(**note_data, id=id, user_id=identity)

        try:
            db.session.add(note)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while trying to create the note")

        return note
