import os

from flask import Flask, jsonify
from flask_smorest import Api
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

from resources.user import blp as UserBlueprint
from resources.note import blp as NoteBlueprint
from redis_server import redis
from db import db
import models


def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.config["API_TITLE"] = "Notes App API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3"
    app.config["OPENAPI_URL_PREFIX"] = "/"
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui"
    app.config[
        "OPENAPI_SWAGGER_UI_URL"
    ] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET")

    db.init_app(app)
    migrate = Migrate(app, db)

    api = Api(app)

    jwt = JWTManager(app)

    @jwt.token_in_blocklist_loader
    def is_token_in_blocklist(jwt_header, jwt_payload):
        return True if redis.sismember("blocklist:jti", jwt_payload["jti"]) else False

    @jwt.revoked_token_loader
    def revoked_token(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked", "error": "token_revoked"}
            ),
            401,
        )

    api.register_blueprint(UserBlueprint)
    api.register_blueprint(NoteBlueprint)

    return app
