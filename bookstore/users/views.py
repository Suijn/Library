from flask import (Blueprint, request, jsonify)
from .models import UserSchema, User, RegisterSchema, LoginSchema
from ..extensions import db, bcrypt
from flask_jwt_extended import create_access_token
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError


blueprint = Blueprint('users', __name__)

user_schema = UserSchema()
users_schema = UserSchema(many=True)

@blueprint.route('/users', methods=['GET'])
@jwt_required()
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

    user = User(password, email)

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
        
    access_token = create_access_token(identity=email)
    return jsonify(access_token)


