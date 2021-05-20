import datetime
from datetime import timedelta
from flask import (Blueprint, request, jsonify, abort)
from .models import UserSchema, User, RegisterSchema, LoginSchema, Role, UpdatePasswordSchema
from ..extensions import db, bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
from ..decorators import require_role, isAdminOrOwner, isOwner


blueprint = Blueprint('auth', __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@blueprint.route('/users', methods=['GET'])
@jwt_required()
@require_role(['Admin'])
def getUsers():
    users = User.query.all()
    payload = users_schema.dump(users)

    return jsonify(payload), 200


@blueprint.route('/user/<id>', methods=['GET'])
@jwt_required()
@require_role(['Admin'])
def getUser(id):
    user = User.get_or_404(id)
    payload = user_schema.dump(user)

    return jsonify(payload), 200


@blueprint.route('/user/<id>', methods=['DELETE'])
@jwt_required()
@require_role(['Admin'])
def removeUser(id):
    user = User.get_or_404(id)

    db.session.delete(user)
    db.session.commit()

    return '', 204


@blueprint.route('/user/changeEmail/<id>', methods=['PATCH'])
@jwt_required()
@require_role(['User'])
@isAdminOrOwner()
def changeUserEmail(id):
    """
    Updates user email.
        An Admin can update every user.
        A Normal user can only update his own email.

    The new email address has to be different from the previous one.
    """
    schema = UserSchema(only=('email',))
    email = request.json['email']  
    user = User.get_or_404(id) 
    
    if user.email == email:
        abort(400, 'The new email address has to be different from the previous one.')

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    user.email = email
    payload = user_schema.dump(user)

    db.session.commit()
    return payload, 200

@blueprint.route('/user/changePassword/<id>', methods=['PATCH'])
@jwt_required()
@require_role(['User'])
@isOwner()
def changeUserPassword(id):
    """
    Updates user password.
        Only the owner of the account can update his password.

        Password must be different from the previous one.
    """

    current_user = User.get_or_404(id)
    schema = UpdatePasswordSchema(user = current_user) 

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    
    password = request.json['password']
    current_user.set_password(password)

    db.session.commit()
    return '', 204


@blueprint.route('/register', methods=['POST'])
def registerUser():
    schema = RegisterSchema()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    password = request.json['password']
    email = request.json['email']

    #A role is created before first user.
    try:
        role = Role.query.filter_by(name='User').one()
    except NoResultFound as err:
        role = Role('User')
   
    user = User(password, email)
    user.roles.append(role)

    db.session.add(user)
    db.session.commit()

    payload = user_schema.dump(user)
    
    return jsonify(payload), 201
    


@blueprint.route('/login', methods=['POST'])
def login():
    schema = LoginSchema()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    new_email = request.json['email']
    password = request.json['password']
    
    user = User.query.filter_by(email=new_email).first()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(access_token = access_token, refresh_token = refresh_token)


@blueprint.route('/refreshToken', methods=['POST'])
@jwt_required(refresh=True)
def refreshToken():
    identity = get_jwt_identity()
    
    access_token = create_access_token(identity = identity)

    return jsonify(access_token=access_token)



