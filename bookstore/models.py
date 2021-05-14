from .extensions import db, ma
from sqlalchemy.orm import relationship
from marshmallow import Schema, fields, validates, ValidationError,validates_schema
from flask import abort

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    pages = db.Column(db.Integer, nullable=True)
    isReserved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates='books')


    def __repr__(self):
        return f'{self.__class__}'
    
    
    def __str__(self):
        return f'id: {self.id}, title: {self.title}'

    
    @classmethod
    def get_or_404(cls, id):
        """
        A class method to get a book from the database.
        Abort if book is None.
        """
        book = Book.query.get(id)
        
        if not book:
            print(book)
            abort(404)
        return book
    
    def __init__(self, title, author):
        self.title = title
        self.author = author


class BookSchema(ma.Schema):
    id = fields.Integer()
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    pages = fields.Integer()
    isReserved = fields.Bool()
    user = fields.Nested("UserSchema", only=("id", "email"))


class BookUpdateSchema(ma.Schema):
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    pages = fields.Integer(required=True)
    isReserved = fields.Bool(required=True)




