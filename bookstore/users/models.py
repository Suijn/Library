from ..extensions import db, ma
from sqlalchemy.orm import relationship
from ..extensions import (bcrypt)
from marshmallow import Schema, fields, validates, ValidationError,validates_schema
from ..models import BookSchema

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.LargeBinary(), nullable=False)
    email= db.Column(db.String(), nullable=False, unique=True)
    books = db.relationship("Book", back_populates='user')

    def __init__(self, password, email):
        self.set_password(password)
        self.email = email

    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    
    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def __repr__(self):
        return f'{self.__class__}'

    
    def __str__(self):
        return f'id: {self.id}, email: {self.email}'


class RegisterSchema(ma.Schema):
    email = fields.Email()
    password = fields.Str()
    password_confirmation = fields.Str()

    @validates_schema
    def validatePassword(self, data, **kwargs):
        '''Validates that passwords match'''
        if data["password"] != data["password_confirmation"]:
            raise ValidationError("Passwords must match")
    
    @validates('email')
    def validateEmailUnique(self, value):
        '''Validates that email is unique'''
        user = User.query.filter_by(email=value).first()

        if user:
            raise ValidationError('Provided email is already in use!')


class LoginSchema(ma.Schema):
    email = fields.Email()
    password = fields.Str()

    @validates_schema
    def userExistsAndPasswordCorrect(self, data, **kwargs):
        '''First validates that the user exists and only then validates the password for the given user'''
        value = data['email']
        password = data['password']

        user = User.query.filter_by(email=value).first()

        if not user:
            raise ValidationError("Wrong credentials!")
        elif not user.check_password(password):
            raise ValidationError("Wrong credentials!")


class UserSchema(ma.Schema):
    id = fields.Integer()
    password = fields.Str()
    email = fields.Email()
    books = fields.Nested(BookSchema, many=True)
    # class Meta:
    #     fields = ('id', 'password', 'email', 'books')