from json import dump
from sqlalchemy.sql.operators import nullsfirst_op
from .extensions import db, ma
from sqlalchemy.orm import backref, relationship
from marshmallow import Schema, fields, validates, ValidationError,validates_schema
from flask import abort
import datetime
from datetime import date
from sqlalchemy import CheckConstraint

def calculate_end_date(start_date):
    """Calculate the date until which the book has to be returned."""
    delta = datetime.timedelta(days=30)
    end_date = start_date + delta
    return end_date


class Book(db.Model):
    """A book model."""
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    pages = db.Column(db.Integer, nullable=True)
    isReserved = db.Column(db.Boolean, default=False)
    reservation = db.relationship('Reservation', backref='book')


    def __init__(self, title, author, pages = 0, isReserved = False):
        self.title = title
        self.author = author
        self.pages = pages
        self.isReserved = isReserved


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


class Reservation(db.Model):
    """A reservation model to store information about books reservations."""
    __tablename__ = 'reservations'
    __table_args__ = (
        CheckConstraint("status IN ('STARTED', 'FINISHED')"),
    )
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    reserved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    status = db.Column('status', db.String, default='STARTED', nullable=False)
    start_date = db.Column(db.Date, default=date.today(), nullable=False)
    expected_end_date = db.Column(db.Date, default=calculate_end_date(date.today()), nullable=False)
    actual_end_date = db.Column(db.Date, default=None, nullable=True)
    was_prolonged = db.Column(db.Boolean, default=False, nullable=False)


class ReservationSchema(ma.Schema):
    """A read-only schema for the Reservation model."""
    book_id = fields.Integer(dump_only=True)
    reserved_by = fields.Integer(dump_only=True)
    status = fields.Str(dump_only=True)
    start_date = fields.Date(dump_only=True)
    expected_end_date = fields.Date(dump_only=True)
    was_prolonged = fields.Bool(dump_only=True)


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


class BookSearchSchema(ma.Schema):
    """A schema to search for books."""
    title = fields.Str(required=True)
    author = fields.Str(required=True)

    @validates_schema
    def validateAtLeastOneFieldPresent(self, data, **kwargs):
        '''Validates there is at least one field filled.'''

        if "title" not in data and "author" not in data:
            raise ValidationError("No title or author.")
        if data["title"].isspace() and data["author"].isspace():
            raise ValidationError("No title or author.")
        if not data["title"] and not data["author"]:
            raise ValidationError("No title or author.")

class BookSearchSchemaAdmin(ma.Schema):
    """A schema to search for books."""
    id = fields.Str(required=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)

    @validates_schema
    def validateAtLeastOneFieldPresent(self, data, **kwargs):
        '''Validates there is at least one field filled.'''

        if "id" not in data and "title" not in data and "author" not in data:
            raise ValidationError("No id, title or author.")
        if not data["id"] and data["title"].isspace() and data["author"].isspace():
            raise ValidationError("No id, title or author.")
        if not data["id"] and not data["title"] and not data["author"]:
            raise ValidationError("No id, title or author.")



