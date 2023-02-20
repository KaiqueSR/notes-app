from flask.views import MethodView
from flask_smorest import Blueprint, abort
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256

from uuid import uuid4

from db import db
from schemas import UserSchema
from models import UserModel

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(201, UserSchema)
    def post(self, user_data):
        id = str(uuid4())
        user = UserModel(id=id, username=user_data["username"], email=user_data["email"], password=pbkdf2_sha256.hash(
            user_data["password"]))

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="An user with that username or email already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while trying to create the user")

        return user
