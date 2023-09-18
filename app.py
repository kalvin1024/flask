from flask import Flask, jsonify
from flask_smorest import Api
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
import secrets
from db import db
from blocklist import BLOCKLIST

# adding __init__ helps the python interpreter to interpret the entire folder as one module
import models
# also letting SQLAlchemy know what models exist in our application because they are db.Model instances,
# look at __tablename__ and define db.Column attrs to create tables

from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint
from resources.tag import blp as TagBlueprint
from resources.user import blp as UserBlueprint

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
    migrate = Migrate(app, db) # using flaks-migrate to create tables would make SQLAlchemy no longer needed
    api = Api(app) # api object derived from the app object, more of App.use(api) in Node
    
    app.config['JWT_SECRET_KEY'] = str(secrets.SystemRandom().getrandbits(128)) # secret key for hashing JWTs to the client, do not expose them in production
    jwt = JWTManager(app)
    
    # JWT claims: e.g. store in JWT whether the user whose ID stored in the JWT is an admin or not
    # check the user's permissions once
    @jwt.additional_claims_loader
    def add_claims_to_jwt(identity):
        # assuming that the user with and ID of 1 will be the administrator. 
        # Normally you'd read this from either a config file or the database.
        if identity == 1:
            return {"is_admin": True}
        return {"is_admin": False}
    
    # catching jwt errors, meant to be callback from the decorator registries
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload): # this assumes a jwt exists, while the two below don't
        return (
            jsonify({"message": "The token has expired.", "error": "token_expired"}),
                401,
        )
        
    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return (
            jsonify({"message": "Signature verification failed.", "error": "invalid_token"}),
            401,
        )
        
    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return (
            jsonify({
                "description": "Request does not contain an access token.", 
                "error": "authorization_required",
            }), 
            401,
        )
    
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload['jti'] in BLOCKLIST
    
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {"description": "The token has been revoked."}
            ), 401
        )
    
    @jwt.needs_fresh_token_loader
    def token_not_fresh_callback(jwt_header, jwt_payload):
        return (
            jsonify(
                {
                    "description": "The token is not fresh.",
                    "error": "fresh_token_required",
                }
            ),
            401,
        )
        
        
    with app.app_context():
        db.create_all() # initiate all resources associated with the database (tables and db itself)
        
    # register API endpoints
    api.register_blueprint(ItemBlueprint)
    api.register_blueprint(StoreBlueprint) 
    api.register_blueprint(TagBlueprint)
    api.register_blueprint(UserBlueprint)
    
    return app