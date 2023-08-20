from flask import Flask, request
app = Flask(__name__)

# temporary storage in memoryd
stores = [{"name": "My Store", "items": [{"name": "my item", "price": 15.99}]}]

# registers the route's endpoint with Flask. That's the /store do,
# and app.get() returns a big decorator function specified to get_stores
@app.get("/store")
def get_stores():
    return {"stores": stores}

@app.post("/store")
def create_store():
    request_data = request.get_json()
    new_store = {"name": request_data['name'], "items":[]}
    stores.append(new_store)
    return new_store, 201 # why just a tuple?

# view function is dynamically routed to <string:name> specifying param=name in string, 
# in express it's just :name, no validation logic except using middleware.
@app.get("/store/<string:name>")
def get_store(name):
    for store in stores:
        if store["name"] == name:
            return store
    return {"message": "Store not found"}, 404

@app.get("/store/<string:name>/item")
def get_item_in_store(name):
    for store in stores:
        if store['name'] == name:
            return {'items': store['items']}
        return {'message': "Store not found"}, 404

@app.post("/store/<string:name>/item")
def create_item(name):
    req_data = request.get_json()
    for store in stores:
        if store['name'] == name:
            new_item = {'name': req_data['name'], 'price': req_data['price']}
            store['items'].append(new_item)
            return new_item
    return {'message': 'Store not found'}, 404

@app.get("/")
def index():
    return "hello you motherfucking bastard!"