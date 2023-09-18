from flask.views import MethodView
from flask_smorest import Blueprint, abort
from passlib.hash import pbkdf2_sha256 # standard algorithm
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt,
    get_jwt_identity,
    jwt_required,
) # JWT

from db import db
from blocklist import BLOCKLIST

from models import UserModel
from schemas import UserSchema

# this does not require a front end register/login page.
blp = Blueprint("Users", "users", description="Operations on users")

@blp.route("/register")
class UserRegister(MethodView):
    
    @blp.arguments(UserSchema)
    @blp.response(201, description="User created successfully")
    def post(self, user_data):
        if UserModel.query.filter(UserModel.username == user_data['username']).first():
            # 409: conflict with existing resource, occurred at PUT and concurrent write
            abort(409, message="A user with that username already existed") 
        
        user = UserModel(username = user_data['username'],
                         password = pbkdf2_sha256.hash(user_data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        return {"message": "User created successfully"}

@blp.route("/login")
class UserLogin(MethodView):
    @blp.arguments(UserSchema)
    @blp.response(200, description="User logged-in successfully and JWT created")
    def post(self, user_data): # not necessarily a POST to database but an authorization validation, hence 200 not 201
        user = UserModel.query.filter(UserModel.username == user_data['username']).first()
        if user and pbkdf2_sha256.verify(user_data['password'], user.password): # hash user entered password again and compare
            # authorized
            access_token = create_access_token(identity=user.id, fresh=True) # create fresh token from login
            refresh_token = create_refresh_token(user.id) # also give the user refresh token
            return {"access token": access_token, "refresh token": refresh_token}
        abort(401, message="Invalid credentials")

@blp.route("/refresh")
class TokenRefresh(MethodView):
    @jwt_required(refresh=True) # require an refresh token to 'refresh' the token
    @blp.response(200, description="Grab a non-fresh JWT access token")
    def post(self):
        current_user = get_jwt_identity() #jwt is already present
        new_token = create_access_token(identity=current_user, fresh=False) #type-II token, non-fresh, cannot go to certain routes
        # when to add the refresh token to the blocklist will depend on the app design
        # jti = get_jwt()['jti'] # register jti to the invalid jwt list after refreshing k times
        # BLOCKLIST.add(jti)
        return {"access_token": new_token}
        
    
@blp.route("/logout")
class UserLogout(MethodView):
    @jwt_required()
    @blp.response(200, description="User logged out successfully and JWT added to blocklist")
    def post(self):
        jti = get_jwt()["jti"]
        BLOCKLIST.add(jti)
        return {"message": "Successfully logged out"}

    
# testing purpose only and do not expose to the user interface  
@blp.route("/user/<int:user_id>")
class User(MethodView):
    
    @blp.response(200, UserSchema)
    def get(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        return user

    @blp.response(204)
    def delete(self, user_id):
        user = UserModel.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return {"message": f"user {user_id} deleted successfully"}
    