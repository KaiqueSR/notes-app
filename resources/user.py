from flask import make_response, json
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jti,
)
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from passlib.hash import pbkdf2_sha256

from uuid import uuid4

from db import db
from schemas import UserRegisterSchema, UserSchema
from models import UserModel
from redis_server import redis

blp = Blueprint("Users", "users", description="Operations on users")


@blp.route("/register")
class UserRegister(MethodView):
    @blp.arguments(UserRegisterSchema)
    @blp.response(201, UserRegisterSchema)
    def post(self, user_data):
        id = str(uuid4())
        user = UserModel(
            id=id,
            username=user_data["username"],
            email=user_data["email"],
            password=pbkdf2_sha256.hash(user_data["password"]),
        )

        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            abort(400, message="An user with that username or email already exists")
        except SQLAlchemyError:
            abort(500, message="An error occurred while trying to create the user")

        return user


@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    def post(self, user_data):
        resp = make_response()
        user = UserModel.query.filter(
            UserModel.username == user_data["username"]
        ).first()

        if user and pbkdf2_sha256.verify(user_data["password"], user.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            refresh_token = create_refresh_token(identity=user.id)

            resp.set_cookie("refresh_token_cookie", refresh_token, httponly=True)

            existant_token = redis.get(f"active_tokens:user:{user.id}:jti")

            if existant_token:
                redis.sadd("blocklist:jti", existant_token)

            redis.set(f"active_tokens:user:{user.id}:jti", get_jti(access_token))

            resp.response = json.dumps({"access_token": access_token})
            return resp

        abort(401, message="Invalid credentials")


@blp.route("/refresh")
class UserRefreshToken(MethodView):
    @jwt_required(refresh=True, locations="cookies")
    def post(self):
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False)

        previous_token = redis.get(f"active_tokens:user:{current_user}:jti")

        if previous_token:
            redis.sadd("blocklist:jti", previous_token)

        redis.set(f"active_tokens:user:{current_user}:jti", get_jti(new_token))

        return {"access_token": new_token}
