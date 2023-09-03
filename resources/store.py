import uuid
from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from db import stores

# This will be shown in the documentation
blp = Blueprint("Stores", "stores", description="Operations on stores")

# MethodViews. These are classes where each method maps to one endpoint.
# each file is an entity/table in the database, associated with an API endpoint

# /store/<string:store_id> route
@blp.route("/store/<string:store_id>")
class Store(MethodView): # endpoint associated to the MethodView class.
    def get(self, store_id):
        try:
            return stores[store_id] # limitation of unable to JOIN
        except KeyError:
            # return {"message": "Store not found"}, 404 
            # use abort() instead of returning the error json manually
            abort(404, message='Store not found')
    
    def delete(self, store_id):
        try:
            del stores[store_id]
            return {"message": "Store deleted."}
        except KeyError:
            abort(404, message="Store not found.")
    
# /store route
@blp.route("/store")
class StoreList(MethodView):
    def get(self):
        return {"stores": list(stores.values())} # flatten
    
    def post(self):
        store_data = request.get_json()
        if 'name' not in store_data:
            abort(400, message="Bad request. Ensure 'name' is included in the json payload")
        for store in stores:
            if store_data['name'] == store['name']:
                abort(400, message=f"Store already exists.")
                
        store_id = uuid.uuid4().hex
        # create the structure of body as dictionary and id wrapping on top level
        new_store = {**store_data, "id": store_id}
        stores[store_id] = new_store # hashmap on store_id
        return new_store
