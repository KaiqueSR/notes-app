from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from uuid import uuid4

from db import db
from models import NoteModel, UserModel
from schemas import NoteSchema, NoteUpdateSchema

blp = Blueprint("Notes", "notes", description="Operations on notes")


@blp.route("/notes")
class UserNoteViewOrCreation(MethodView):
    @jwt_required()
    @blp.response(200, NoteSchema(many=True))
    def get(self):
        identity = get_jwt_identity()

        user = UserModel.query.get_or_404(identity)

        return user.notes

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


@blp.route("/notes/<string:note_id>")
class NoteViewOrUpdate(MethodView):
    @jwt_required()
    @blp.arguments(NoteUpdateSchema)
    @blp.response(200, NoteSchema)
    def put(self, note_data, note_id):
        identity = get_jwt_identity()

        note = NoteModel.query.get(note_id)

        if note:
            if note.user_id != identity:
                abort(403, message="This note is not yours")

            note.title = note_data["title"] if "title" in note_data else note.title
            note.content = note_data["content"] if "content" in note_data else note.content
        else:
            note = NoteModel(id=note_id, user_id=identity, **note_data)

        try:
            db.session.add(note)
            db.session.commit()
        except IntegrityError:
            abort(400, message="When creating an object via PUT method, the title should not be null.")
        except SQLAlchemyError:
            abort(500, message="An error occurred while trying to update the note")

        return note
        
    @jwt_required()
    @blp.response(200, NoteSchema)
    def get(self, note_id):
        identity = get_jwt_identity()

        note = NoteModel.query.get_or_404(note_id)
        
        if note.user_id != identity:
            abort(403, message="This note is not yours")

        return note