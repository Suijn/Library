from json import dump
from sqlalchemy.sql.operators import nullsfirst_op
from .extensions import db, ma
from sqlalchemy.orm import backref, load_only, relationship
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
    pages = db.Column(db.Integer, default =0)
    isReserved = db.Column(db.Boolean, default=False)
    reservation = db.relationship('Reservation', backref='book')


    def __repr__(self):
        return f'{self.__class__}'
    
    
    def __str__(self):
        return f'id: {self.id}, title: {self.title}, pages: {self.pages}, isReserved: {self.isReserved}'

    
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
    pages = fields.Integer(default=0)
    isReserved = fields.Bool(dump_only=True)


class BookUpdateSchema(ma.Schema):
    title = fields.Str(required=True, load_only=True)
    author = fields.Str(required=True, load_only=True)
    pages = fields.Integer(required=True, load_only=True)
    isReserved = fields.Bool(required=True, load_only=True)


class BookSearchSchema(ma.Schema):
    """A schema to search for books."""
    title = fields.Str(default='', load_only=True)
    author = fields.Str(default='', load_only=True)

    @validates_schema
    def validateAtLeastOneFieldFilled(self, data, **kwargs):
        '''
        Validates there is at least one field filled.
        
        If there is only only one field filled, check:
            If it consists of only whitespaces - raise Validation error.
            If it is empty - raise Validation error.
        '''

        if "title" not in data and "author" not in data:
            raise ValidationError("No title or author.")
        
        if "title" or "author" in data:
            #There is only one item in the dictionary.
            for field, value in data.items():
                #If value consists of only whitespaces or is empty - raise Validation error.
                if value.isspace() or not value:
                    raise ValidationError("No title or author.")     

        if "title" in data and "author" in data:
            #Raise Validation error if both fields consist of only whitespaces.
            if data["title"].isspace() and data["author"].isspace():
                raise ValidationError("No title or author.")
            #Raise Validation error if both fields are empty.
            if not data["title"] and not data["author"]:
                raise ValidationError("No title or author.")

class BookSearchSchemaAdmin(ma.Schema):
    """A schema to search for books."""
    id = fields.Str()
    title = fields.Str()
    author = fields.Str()

    @validates_schema
    def validate_at_least_one_field_filled(self, data, **kwargs):
        '''Validates there is at least one field filled.'''

        #If no field is filled - raise Validation error.
        if "id" not in data and "title" not in data and "author" not in data:
            raise ValidationError("No id, title or author.")

        if 'id' in data or 'title' in data or 'author' in data:
            #Get the number of keys in the dictionary
            counter = 0

            #Find at least one field filled.
            for key, value in data.items():
                if not value.isspace() and value:
                    counter += 1

            if counter == 0:
                raise ValidationError("No id, title or author.")
    




