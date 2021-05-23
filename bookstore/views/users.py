"""A view module for users to use the library."""
from flask import (Blueprint, jsonify, request, abort)
from ..extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from ..users.models import User
from ..models import (Book, BookSchema, Reservation, ReservationSchema, BookSearchSchema)
from ..decorators import require_role, didReserveBook
from marshmallow import ValidationError
from sqlalchemy.exc import NoResultFound
import datetime

blueprint = Blueprint('users', __name__, url_prefix='/users')

book_schema = BookSchema()
books_schema = BookSchema(many=True)

@blueprint.route('/getReservations', methods=['GET'])
@jwt_required()
@require_role()
def getUserReservations():
    """Get current user reservations."""
    current_user = User.get_or_404(get_jwt_identity())

    reservations = Reservation.query.join(Book).filter(
        Reservation.reserved_by == current_user.id,
        Reservation.status == 'STARTED'
    ).all()

    schema = ReservationSchema(many=True)

    payload = schema.dump(reservations)
    return jsonify(payload), 200


@blueprint.route('/searchBooks', methods=['POST'])
@jwt_required()
@require_role()
def searchForBooks():
    """
    A search utility for users to search for books by title and author.
    
    At least one field is required, if one field is empty - match anything.
    """
    schema = BookSearchSchema()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400


    #Remove additional whitespace's
    #If field is empty - match anything.
    try:
        book_title = "%{}%".format(request.json['title'].strip())
    except KeyError:
        book_title = "%{}%".format('')

    try:
        book_author = "%{}%".format(request.json['author'].strip())
    except KeyError:
        book_author = "%{}%".format('')

        
    books = Book.query.filter(
        Book.title.like(book_title), 
        Book.author.like(book_author)
    ).all()

    payload = books_schema.dump(books)
    return jsonify(payload), 200

@blueprint.route('/book/<id>', methods=['GET'])
@jwt_required()
@require_role()
def getBook(id):
    """Get a book by ID."""
    book = Book.get_or_404(id)
    payload = book_schema.dump(book)

    return jsonify(payload), 200    


@blueprint.route('/reserveBook/<id>', methods=['POST'])
@jwt_required()
@require_role()
def reserveBook(id):
    """
    Reserve a book for the given user.
    
    A single user can reserve up to 5 books.
    """
    current_user = User.get_or_404(get_jwt_identity())
    book = Book.get_or_404(id)

    if book.isReserved == False:
        if current_user.books_amount < 5:
            current_user.books_amount += 1
            book.isReserved = True

            reservation = Reservation()
            reservation.user = current_user
            reservation.book = book

            db.session.add(reservation)
            db.session.commit()
            
            return '', 204
        else:
            abort(400, 'You cannot reserve more books.')
    else:
        abort(400, 'This book is already reserved.')


@blueprint.route('/prolongBook/<book_id>', methods=['PATCH'])
@jwt_required()
@require_role()
@didReserveBook()
def prolong_book(book_id):
    """
    Prolong the book reservation.

    A book reservation can be prolonged only once for the duration of 30 days.
    
    :param book_id: The book the user wants to prolong the reservation for.

    :permission require_role: Requires a role passed in parameter to access this resource.
    :permission didReserveBook: Only the user that reserved the book can ask for the prolongment.
    """

    current_user = User.get_or_404(get_jwt_identity())

    try:
        reservation = Reservation.query.filter(
            Reservation.reserved_by == current_user.id,
            Reservation.book_id == book_id,
            Reservation.status == 'STARTED'
        ).one()
    except NoResultFound:
        abort(401)
    
    if reservation.was_prolonged == False:
        delta = datetime.timedelta(days=30)
        reservation.expected_end_date += delta
        reservation.was_prolonged = True

        db.session.commit()
    else:
        abort(400, 'You have already prolonged the book reservation!')

    return '', 204


