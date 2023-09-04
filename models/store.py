from db import db 

class StoreModel(db.Model):
    __tablename__ = "stores"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    tags = db.relationship("TagModel", back_populates="store", lazy="dynamic")
    items = db.relationship("ItemModel", back_populates="store", lazy="dynamic")
    # same thing here, for each ItemModel will have attribute named store
    # marking lazy=dynamic, items resolves to SQLAlchemy Query instance,
    # + load speed, - actually accessing items, + filtering before loading
    # cascade="all, delete" makes deleting the store also deleting the items related (having foreign key) to the store
    # by default, deleting a store that is referred by fkey in an item is not permitted because foreign key cannot refer to null
    
    # e.g. get all items: store.items.all()
    # filtering: store.items.filter_by(name=='Chair').first()