from json import dump
from sqlalchemy.sql.operators import nullsfirst_op
from .extensions import db, ma
from sqlalchemy.orm import backref, load_only, relationship
from marshmallow import Schema, fields, validates, ValidationError,validates_schema,pre_load
from flask import abort
from datetime import date
from sqlalchemy import CheckConstraint
from bookstore.utils import calculate_end_date


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
    """A book schema."""
    id = fields.Integer()
    title = fields.Str(required=True)
    author = fields.Str(required=True)
    pages = fields.Integer(default=0)
    isReserved = fields.Bool(dump_only=True)


class BookUpdateSchema(ma.Schema):
    """A book update schema."""
    title = fields.Str(required=True, load_only=True)
    author = fields.Str(required=True, load_only=True)
    pages = fields.Integer(required=True, load_only=True)
    isReserved = fields.Bool(required=True, load_only=True)


class BookSearchSchema(ma.Schema):
    """A schema to search for books."""
    title = fields.Str(missing='', load_only=True)
    author = fields.Str(missing='', load_only=True)

    @pre_load
    def trim_leading_trailing_whitespaces(self, data, **kwargs):
        """
        Remove leading and trailing whitespaces from the data before loading the schema.
        """
        if not data:
            raise ValidationError("No title or author.")  

        for key, value in data.items():
            data[key] = value.strip()
        return data  
    

    @validates_schema
    def validateAtLeastOneFieldFilled(self, data, **kwargs):
        '''Validates there is at least one field filled.'''

        if not data['title'] and not data['author']:
            raise ValidationError("No title or author.")
        else:
            #Assert there is at least one field filled, otherwise raise validation error.
            counter = 0
            for key, value in data.items():
                if not value.isspace() and value:
                    counter += 1

            if counter == 0:
                raise ValidationError("No title or author.")


class BookSearchSchemaAdmin(ma.Schema):
    """A schema to search for books."""
    id = fields.Int(load_only=True)
    title = fields.Str(load_only=True)
    author = fields.Str(load_only=True)


    @pre_load
    def trim_leading_trailing_whitespaces(self, data, **kwargs):
        """
        Remove leading and trailing whitespaces from the data before loading the schema.
        """
        if not data:
            raise ValidationError("No id, title or author.")  

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data


    @validates_schema
    def validate_at_least_one_field_filled(self, data, **kwargs):
        '''Validates there is at least one field filled.'''

        #If no field is filled - raise Validation error.
        if "id" not in data and "title" not in data and "author" not in data:
            raise ValidationError("No id, title or author.")

        if 'id' in data or 'title' in data or 'author' in data:
            counter = 0

            #Assert, there is at least one field filled, otherwise raise validation error.
            for key, value in data.items():
                if isinstance(value, int):
                    if value:
                        counter +=1
                if isinstance(value, str):
                    if not value.isspace() and value:
                        counter += 1

            if counter == 0:
                raise ValidationError("No id, title or author.")

class GetReservationSchema(ma.Schema):
    """A schema to search for reservations."""
    status = fields.Str(missing=None, load_only=True)
    reserved_by = fields.Int(missing=None, load_only=True)
    book_id = fields.Int(missing=None, load_only=True)

    @pre_load
    def trim_leading_trailing_whitespaces(self, data, **kwargs):
        """Trim leading and trailing whitespaces before loading."""
        if not data:
            raise ValidationError("No status, user or book.")  

        for key, value in data.items():
            if isinstance(value, str):
                data[key] = value.strip()
        return data
    
    
    @validates_schema
    def validate_at_least_one_field_filled(self, data, **kwargs):
        """Validate at least one field is filled."""
        if not data:
            raise ValidationError("No status, user or book.") 

        counter = 0 # a counter to count properly filled fields.
        for key, value in data.items():
            if isinstance(value, int):
                if value:
                    counter+=1
            elif isinstance(value, str):
                if value and not value.isspace():
                    counter += 1
        
        if counter == 0:
            raise ValidationError('No status, user or book.')
        




