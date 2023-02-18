import os

from flask import Flask
from flask_migrate import Migrate
from dotenv import load_dotenv

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
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")

    db.init_app(app)
    migrate = Migrate(app, db)

    @app.before_first_request
    def create_tables():
        db.create_all()

    @app.route("/")
    def hello():
        return {"message": "Hello, World!"}

    return app
