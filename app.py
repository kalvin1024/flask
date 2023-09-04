from flask import Flask
from flask_smorest import Api
import os

from db import db

# adding __init__ helps the python interpreter to interpret the entire folder as one module

import models
# also letting SQLAlchemy know what models exist in our application because they are db.Model instances,
# look at __tablename__ and define db.Column attrs to create tables

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint

# app factory method
def create_app(db_url=None):
    app = Flask(__name__) # name of the python module
    app.config["API_TITLE"] = "Stores REST API"
    app.config["API_VERSION"] = "v1"
    app.config["OPENAPI_VERSION"] = "3.0.3" # OpenAPI dependency 
    app.config["OPENAPI_URL_PREFIX"] = "/" # no prefix
    
    # swagger ui webpage that is easy to know to the users
    app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" 
    app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
    
    # sqlalchemy related configs
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url or os.getenv("DATABASE_URL", "sqlite:///data.db")
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    api = Api(app) # api object derived from the app object
    # register API endpoints
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint) 
    api.register_blueprint(TagBlueprint)
    
    return app