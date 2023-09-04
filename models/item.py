from db import db

# every model inherits from db.Model and more properties to interact db thru model such as query
class ItemModel(db.Model):
    __tablename__ = "items"
    # no fields allow null here
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)
    
    store = db.relationship("StoreModel", back_populates="items")
    # this means for each store will have attribute 'items' = list of ItemModel instances
    # back_populates indicate a bidirectional relationship between 2 mapped class for 1-many or many-many relationships
    tags = db.relationship("TagModel", back_populates="items", secondary="item_tags")