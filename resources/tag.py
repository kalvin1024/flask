from flask.views import MethodView
from flask_smorest import Blueprint, abort

from schemas import TagSchema, ItemTagSchema
from db import db
from models import TagModel, StoreModel, ItemModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

blp = Blueprint("Tags", "tags", description="Operations on tags")

@blp.route("/store/<string:store_id>/tag")
class TagInStore(MethodView): # tag cannot exist independently without a store
    @blp.response(200, TagSchema(many=True))
    def get(self, store_id):
        store = StoreModel.query.get_or_404(store_id)
        return store.tags.all() # SELECT tags FROM stores JOIN tags WHERE stores.id = store_id
    
    @blp.arguments(TagSchema) # register to the tag schema when data into here
    @blp.response(201, TagSchema)
    def post(self, tag_data, store_id):
        # has duplicated name and store_id affiliation, cannot be caught by IntegrityError due to Schema, must hard compare
        if TagModel.query.filter(TagModel.store_id == store_id, TagModel.name == tag_data['name']).first():
            abort(409, message="A tag with that name already exists in that store.") 
            
        tag = TagModel(**tag_data, store_id = store_id)
        try:
            db.session.add(tag)
            db.session.commit()
        except SQLAlchemyError as e:
            abort(500, message=str(e))
            
        return tag

@blp.route("/item/<string:item_id>/tag/<string:tag_id>")
class LinkTagsToItem(MethodView): # only do the action in the secondary table
    @blp.response(201, TagSchema)
    def post(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.append(tag)  # this action also insert the row to secondary table
        
        try:
            db.session.add(item) # this line adds item to the tag's items list
            db.session.commit()
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag")
        return tag
    
    @blp.response(200, ItemTagSchema)
    def delete(self, item_id, tag_id):
        item = ItemModel.query.get_or_404(item_id)
        tag = TagModel.query.get_or_404(tag_id)
        item.tags.remove(tag) # this action also delete the row to secondary table
        try:
            db.session.delete(item) # this action deletes tag's reference to item
            db.session.commit() 
        except SQLAlchemyError:
            abort(500, message="An error occurred while inserting the tag")
    
        # this json object is being returned from this delete method with the ItemTagSchema format
        return {"message": "Item removed from the tag", "item": item, "tag": tag}
    
    
@blp.route("/tag/<string:tag_id>")
class Tag(MethodView):
    @blp.response(200, TagSchema)
    def get(self, tag_id): # simply get the single tag associated with the id
        tag = TagModel.query.get_or_404(tag_id)
        return tag

    @blp.response(202, 
                  description="Deletes a tag if no item is tagged with it",
                  example={"message":"Tag deleted."}
    ) # example is an example of successful operation
    @blp.alt_response(404, description="Tag not found") # behaviors in other situations
    @blp.alt_response(400, description="returned if the tag is assigned to no one or more items. In this case, the tag is not deleted.")
    def delete(self, tag_id):
        tag = TagModel.query_or_get_404(tag_id)
        if not tag.items: # if tag's items are empty
            db.session.delete(tag)
            db.session.commit() # safely proceed
            return {"message": "tag deleted."}
        
        abort(
            400,
            message="Could not delete tag. Make sure tag is not associated with any items, then try again.",
        )
