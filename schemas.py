from marshmallow import Schema, fields # library to serialize our data records as json & backward

# avoid infinite nesting, letting the schema only nesting non-recursive fields
class PlainItemSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    price = fields.Float(required=True)

class PlainStoreSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()

class PlainTagSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str()
    
class ItemSchema(PlainItemSchema):
    # load_only is skipped during serialization and is write-only, dump_only is read-only
    # fkeys are not serialized back to the response
    store_id = fields.Int(required=True, load_only=True)
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)
    
class StoreSchema(PlainStoreSchema):
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    tags = fields.List(fields.Nested(PlainTagSchema()), dump_only=True)
    
class TagSchema(PlainTagSchema):
    store_id = fields.Int(load_only=True)
    # each tag has at most 1 store to affiliate
    store = fields.Nested(PlainStoreSchema(), dump_only=True)
    items = fields.List(fields.Nested(PlainItemSchema()), dump_only=True)
    
class ItemTagSchema(Schema):
    message = fields.Str()
    item = fields.Nested(ItemSchema) # link to item object, fkey
    tag = fields.Nested(TagSchema)
    
# update schema
# defining only fields relevant to update and include in the PUT payload
class ItemUpdateSchema(Schema):
    name = fields.Str()
    price = fields.Float() # no required, can come partially
    # no ids because these are immutable to PUT
    
# user schema
class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)
    password = fields.Str(required=True, load_only=True) # sensitive field protected from sending response back
    
class UserRegisterSchema(UserSchema):
    # ask user to provide email when register, not when login
    email = fields.String(required=True)