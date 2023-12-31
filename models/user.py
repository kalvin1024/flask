from db import db 

class UserModel(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False) # do not require password be unique to each other, hashed = length 256
    email = db.Column(db.String, unique=True, nullable=False)
    