from flask import Flask
from flask_smorest import Api
from resources.item import blp as ItemBlueprint
from resources.store import blp as StoreBlueprint

app = Flask(__name__) # name of the python module
app.config["API_TITLE"] = "Stores REST API"
app.config["API_VERSION"] = "v1"
app.config["OPENAPI_VERSION"] = "3.0.3" # OpenAPI dependency 
app.config["OPENAPI_URL_PREFIX"] = "/" # no prefix
app.config["OPENAPI_SWAGGER_UI_PATH"] = "/swagger-ui" 
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
# swagger ui webpage that is easy to know to the users

api = Api(app) # api object derived from the app object

api.register_blueprint(ItemBlueprint)
api.register_blueprint(StoreBlueprint) # register API endpoints