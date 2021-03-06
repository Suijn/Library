"""Models module."""
from os import name
from ..extensions import db, ma
from sqlalchemy.orm import backref, load_only, relationship
from ..extensions import (bcrypt)
from marshmallow import Schema, fields, validates, ValidationError,validates_schema
from ..models import BookSchema
from flask import abort
from sqlalchemy import CheckConstraint


# Associate table for users and roles
roles_users = db.Table('roles_users',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'))
)


class Role(db.Model):
    """A role for users."""
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    users = db.relationship("User", secondary=roles_users, backref='roles')

    
    def __str__(self):
        return f'Role: {name}'


    def __repr__(self):
        return f'{self.__class__}'


class RoleSchema(ma.Schema):
    name = fields.Str()
    user_identification = fields.Nested("UserSchema", only=("id",), many=True)


class User(db.Model):
    """A user model."""
    __tablename__ = 'users'
    __table_args__ = (
        CheckConstraint("books_amount <= 5"),
    )
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.LargeBinary(), nullable=False)
    email= db.Column(db.String(), nullable=False, unique=True)
    books_amount = db.Column(db.Integer, default=0, nullable=False)
    reservations = db.relationship("Reservation", backref='user')

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.set_password(kwargs['password'])
        user_role = Role.query.filter(Role.name == 'User').one()
        self.roles.append(user_role)

    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    
    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def has_roles(self, roles):
        user_roles = [x.name for x in self.roles]

        return set(roles).issubset(set(user_roles))
    
    def has_role(self, role):
        user_roles = [x.name for x in self.roles]

        return role in user_roles

    @classmethod
    def get_or_404(cls, id):
        """
        A class method to get a user from the database.
        Abort if user is None.
        """
        user = User.query.get(id)

        if not user:
            abort(404)
        return user
            

    def __repr__(self):
        return f'{self.__class__}'

    
    def __str__(self):
        return f'id: {self.id}, email: {self.email}'


class RegisterSchema(ma.Schema):
    email = fields.Email(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)
    password_confirmation = fields.Str(required=True, load_only=True)

    @validates_schema
    def validatePassword(self, data, **kwargs):
        '''Validates that passwords match.'''

        if data["password"] != data["password_confirmation"]:
            raise ValidationError("Passwords must match")
    
    @validates('email')
    def validateEmailUnique(self, value):
        '''Validates that email is unique.'''

        user = User.query.filter_by(email=value).first()

        if user:
            raise ValidationError('Provided email is already in use!')


class LoginSchema(ma.Schema):
    email = fields.Email(required=True, load_only=True)
    password = fields.Str(required=True, load_only=True)

    @validates_schema
    def userExistsAndPasswordCorrect(self, data, **kwargs):
        '''First validates that the user exists and only then validates the password for the given user.'''

        value = data['email']
        password = data['password']

        user = User.query.filter_by(email=value).first()

        if not user:
            raise ValidationError("Wrong credentials!")
        elif not user.check_password(password):
            raise ValidationError("Wrong credentials!")



    
class UserSchema(ma.Schema):
    """A schema for user."""
    id = fields.Integer()
    email = fields.Email()
    books_amount = fields.Integer()
    roles = fields.Nested(RoleSchema, many=True)

    @validates('email')
    def validateEmailUnique(self, value):
        '''Validates that email is unique.'''
        user = User.query.filter_by(email=value).first()

        if user:
            raise ValidationError('Provided email is already in use!')



class UpdatePasswordSchema(ma.Schema):
    """Schema to update user password."""
    password = fields.Str(required=True, load_only=True)
    password_confirmation = fields.Str(required=True, load_only=True)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user') if 'user' in kwargs else None
        super().__init__(*args,**kwargs)

    @validates_schema
    def validatePassword(self, data, **kwargs):
        '''
        Validates that passwords match.
        Validates that the new password is different from the previous one
        '''

        if data["password"] != data["password_confirmation"]:
            raise ValidationError("Passwords must match")
        if self.user.check_password(data["password"]):
            raise ValidationError("Password must be different from the previous one.")

