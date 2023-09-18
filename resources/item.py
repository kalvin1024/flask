from flask import request
from flask.views import MethodView
from flask_smorest import Blueprint, abort
from flask_jwt_extended import jwt_required, get_jwt # resource protection

from schemas import ItemSchema, ItemUpdateSchema
from db import db
from models import ItemModel
from sqlalchemy.exc import SQLAlchemyError

blp = Blueprint("Items", "items", description="Operations on items")

# for demonstration purpose, only protecting Item resource to login users
@blp.route("/item/<string:item_id>")
class Item(MethodView):
    # route marked with jwt_required would have request header Content-Type: Authorization and application/json: Bearer <jwt>
    # the jwt is returned from user /login route
    @jwt_required() 
    @blp.response(200, ItemSchema) # with this decorator, validate as ItemSchema, documentation updated and wrap response 200
    def get(self, item_id):
        # try:
        #     return items[item_id]
        # except KeyError:
        #     abort(404, message="Item not found.")
        # this method also couples the 404 no found into the flow
        item = ItemModel.query.get_or_404(item_id) 
        return item 
        
    @jwt_required()
    @blp.response(204)
    def delete(self, item_id):
        jwt = get_jwt()
        if not jwt.get("is_admin"): # field stored in the app.py:add_claims_to_jwt()
            abort(401, message="Admin privilege required to delete items.")
        
        item = ItemModel.query.get_or_404(item_id)
        db.session.delete(item) # DELETE FROM Items WHERE id = item_id
        db.session.commit()
        return {"message" : "Item deleted."}

    @jwt_required(fresh=True)
    @blp.arguments(ItemUpdateSchema) # register to the update schema 
    @blp.response(200, ItemSchema)
    def put(self, item_data, item_id): # item_data the injected data always come before url argument <item_id>
        # uses update-or-insert as if in the raw dictionary
        item = ItemModel.query.get_or_404(item_id)
        if item:
            if 'price' in item_data: # field-wise validation, replaced by more concise code if item_data has k fields
                item.price = item_data['price']
            if 'name' in item_data:
                item.name = item_data['name']
        else:
            item = ItemModel(id=item_id, **item_data)
            
        db.session.add(item)
        db.session.commit()
        
        return item

@blp.route("/item")
class ItemList(MethodView):
    @jwt_required() 
    @blp.response(200, ItemSchema(many=True)) # return multiple instances to be validated
    def get(self):
        return ItemModel.query.all() # this queries all items in the Items table, equiv to SELECT * FROM Items

    @jwt_required(fresh=True)
    @blp.arguments(ItemSchema)
    @blp.response(201, ItemSchema) # 201 signifies POST request success
    def post(self, item_data):
        # for item in items.values():
        #     if (
        #         item_data["name"] == item["name"]
        #         and item_data["store_id"] == item["store_id"]
        #     ):
        #         abort(400, message=f"Item already exists.")
        
        # item_id = uuid.uuid4().hex
        # item = {**item_data, "id": item_id}
        # items[item_id] = item
        
        # all duplication and uuid assignments are taking cared by ItemModel() in db/item.py
        item = ItemModel(**item_data) # decoupling the entries in item_data to args in ItemModel
        try:
            db.session.add(item) # INSERT INTO Items (col1, col2, col3, ...) VALUES (val1, val2, val3...)
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the item.")

        return item