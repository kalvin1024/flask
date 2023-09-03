from flask import Flask, request
from flask_smorest import abort
from db import stores, items # subject to change
import uuid

app = Flask(__name__) # name of the python module

@app.get("/")
def index():
    return "hello you cute little fluffy baby!"

# registers the route's endpoint with Flask. That's the /store do,
# and app.get() returns a big decorator function specified to get_stores
@app.get("/store")
def get_stores():
    return {"stores": list(stores.values())} # flatten

@app.post("/store")
def create_store():
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

# view function is dynamically routed to <string:name> specifying param=name in string, 
# in express it's just :name, no validation logic except using middleware.
@app.get("/store/<string:name>")
def get_store(store_id):
    try:
        return stores[store_id] # limitation of unable to JOIN
    except KeyError:
        # return {"message": "Store not found"}, 404 
        # use abort() instead of returning the error json manually
        abort(404, message='Store not found')
        
@app.delete("/store/<string:store_id>")
def delete_store(store_id):
    try:
        del stores[store_id]
        return {"message": "Store deleted."}
    except KeyError:
        abort(404, message="Store not found.")
        
@app.get("/items")
def get_all_items():
    return {"items": list(items.values())}

@app.get("/item/<string:item_id>")
def get_item(item_id):
    try:
        return items[item_id]
    except KeyError:
        abort(404, message='Item not found')
        
@app.post("/item")
def create_item(item):
    item_data = request.get_json()
    # validate fields exist
    if (
        'price' not in item_data or
        'store_id' not in item_data or
        'name' not in item_data
    ): 
        abort(400, message="Bad request, ensure fields are included in json payload properly.")
    
    # validate duplication (on entirety)
    for item in items.values():
        if (
            item_data['name'] == item['name'] and item_data['store_id'] == item['store_id']
        ):
            abort(400, message=f"Item already exists, {item_data}")
    
    item_id = uuid.uuid4().hex
    # copy and write
    new_item = {**item_data, 'id': item_id}
    items[item_id] = new_item
    return new_item

@app.put("item/<string:item_id>")
def update_item(item_id):
    item_data = request.get_json()
    if (
        'price' not in item_data or
        'store_id' not in item_data or
        'name' not in item_data
    ): 
        abort(400, message="Bad request, ensure fields are included in json payload properly.")
    try:
        item = items[item_id]
        item |= item_data 
        # | is a dictionary operator in python3.9 used for merging 2 dictionaries, where x | y means if x, y have same field, y field value overwrites x's.
        # and |= is shorthand ofr item = item | item_data
        # natural for a PUT request
        return item
    except KeyError:
        abort(404, message='Item not found')
    

@app.delete("item/<string:item_id>")
def delete_item(item_id):
    try:
        del items[item_id] # dict hashmap operation
        return {"message" : "Item deleted."}
    except KeyError:
        abort(404, message="Item not found.")