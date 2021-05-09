from flask import (Blueprint, request, jsonify)
from .models import UserSchema, User, RegisterSchema, LoginSchema, Role
from ..extensions import db, bcrypt
from flask_jwt_extended import create_access_token, create_refresh_token
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
from ..decorators import require_role


blueprint = Blueprint('users', __name__)

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
def getUser(id):
    user = User.query.get(id)
    payload = user_schema.dump(user)

    return payload, 200


@blueprint.route('/user/<id>', methods=['DELETE'])
@jwt_required()
def removeUser(id):
    user = User.query.get(id)

    if not user:
        raise Exception('An Error happened while removing the user')
    payload = user_schema.dump(user)

    db.session.delete(user)
    db.session.commit()

    return payload, 200


@blueprint.route('/register', methods=['POST'])
def registerUser():
    schema = RegisterSchema()
    password = request.json['password']
    email = request.json['email']

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    """A role is created before first user"""
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
    email = request.json['email']
    password = request.json['password']

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages
    
    user = User.query.filter_by(email=email).first()

    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)

    return jsonify(access_token = access_token, refresh_token = refresh_token)


@blueprint.route('/refreshToken', methods=['POST'])
@jwt_required(refresh=True)
def refreshToken():
    identity = get_jwt_identity()
    
    access_token = create_access_token(identity = identity)

    return jsonify(access_token=access_token)



