import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort

from schemas import StoreSchema
from db import db
from models import StoreModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

# This will be shown in the documentation
blp = Blueprint("Stores", "stores", description="Operations on stores")

# MethodViews. These are classes where each method maps to one endpoint.
# each file is an entity/table in the database, associated with an API endpoint

# /store/<string:store_id> route
@blp.route("/store/<string:store_id>")
class Store(MethodView): # endpoint associated to the MethodView class.
    @blp.response(200, StoreSchema)
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store
    
    @blp.response(204)
    def delete(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        db.session.delete(store)
        db.session.commit()
        return {"message": "Store deleted"}
    
# /store route
@blp.route("/store")
class StoreList(MethodView):
    
    @blp.response(200, StoreSchema(many=True))
    def get(self):
        return StoreModel.query.all()
    
    @blp.arguments(StoreSchema)
    @blp.response(201, StoreSchema)
    def post(self, store_data):
        store = StoreModel(**store_data)
        try:
            db.session.add(store)
            db.session.commit()
        except IntegrityError: # validate duplications because unique=True is raised in Schema definition
            abort(
                400,
                message="A store with that name already exists.",
            )
        except SQLAlchemyError:
            abort(500, message="An error occurred creating the store.")

        return store
