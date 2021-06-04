"""A view module for admins to manage users, books and reservations."""
from copy import error
from flask import (Blueprint, jsonify, request, abort)
from sqlalchemy.sql.expression import true
from ..models import (Book, GetReservationSchema, Reservation, BookSchema, BookSearchSchemaAdmin, BookUpdateSchema, ReservationSchema)
from ..decorators import require_role
from flask_jwt_extended import jwt_required
from ..extensions import db
from marshmallow import ValidationError, fields
from ..users.models import User
from datetime import date

blueprint = Blueprint('admin', __name__, url_prefix='/admin')

book_schema = BookSchema()
books_schema = BookSchema(many=True)

@blueprint.route('/books', methods=['GET'])
@jwt_required()
@require_role(['Admin'])
def get_books():
    books = Book.query.all()
    payload = books_schema.dump(books)

    return jsonify(payload), 200


@blueprint.route('/book', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def add_book():
    try:
        book_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    title = request.json['title'] 
    author = request.json['author']

    book = Book(title=title, author=author)
    if 'pages' in request.json:
        book.pages = request.json['pages']
    
    db.session.add(book)
    db.session.commit()

    payload = book_schema.dump(book)

    return payload, 201

@blueprint.route('/book/<id>', methods=['PUT'])
@jwt_required()
@require_role(['Admin'])
def update_book(id):
    book = Book.get_or_404(id)
    schema = BookUpdateSchema(many=False)

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    book.title = request.json['title']
    book.author = request.json['author']
    book.pages = request.json['pages']
    book.isReserved = request.json['isReserved']

    db.session.commit()
    payload = book_schema.dump(book)

    return payload, 200


@blueprint.route('/book/<id>', methods=['DELETE'])
@jwt_required()
@require_role(['Admin'])
def delete_book(id):
    book = Book.get_or_404(id)

    db.session.delete(book)
    db.session.commit()

    return '', 204


@blueprint.route('/searchBooks', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def search_for_books():
    """
    Book search engine for admin users.
    
    If book_id is sent in request -- return the book with the given id.
    If book_id is not sent in request -- continue the search using the title and author fields.
    """
    schema = BookSearchSchemaAdmin()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    
    # #If id is filled, return the book with the given id.
    if 'id' in request.json:
        if request.json['id']:
            book_id = request.json['id']
            book = Book.get_or_404(book_id)
            payload = book_schema.dump(book)
            return payload, 200
    
    query = Book.query

    for key, value in request.json.items():
        query = query.filter(
            getattr(Book, key).like(f'%{value}%')
        )

    books = query.all()

    payload = books_schema.dump(books)
    return jsonify(payload), 200


@blueprint.route('/reserveBook/<book_id>/<user_id>', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def reserve_book(book_id, user_id):
    """
    Reserve a book for a user.
    
    :param book_id: The book to reserve. 
    :param user_id: The user that reserves the book.

    :if selected book is already reserved -- abort.
    """
    book = Book.get_or_404(book_id)
    current_user = User.get_or_404(user_id)

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
            abort(400, 'User cannot reserve more books.')
    else:
        abort(400, 'This book is already reserved.')


@blueprint.route('/cancelResBook/<book_id>', methods=['PATCH'])
@jwt_required()
@require_role(['Admin'])
def cancel_reservation(book_id):
    """
    Cancel reservation of a book for the given user.
    
    :param book_id: The book which reservation is to be cancelled.
    """
    book = Book.get_or_404(book_id)

    #Get reservation of the book.
    reservation = Reservation.query.filter(
        Reservation.book_id == book.id,
        Reservation.status == 'STARTED'
    ).one()

    #Get user and decrement books_amount.
    user = User.get_or_404(reservation.reserved_by)
    user.books_amount -= 1

    #Change reservation status to finished and book boolean to False.
    book.isReserved = False
    reservation.status = 'FINISHED'

    #Get current date and store it in the database.
    reservation.actual_end_date = date.today()

    db.session.commit()

    return '', 204


@blueprint.route('/getReservations', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def get_reservations():
    """
    Run a search on reservations based on data sent in request.
    """
    schema = GetReservationSchema()

    try:
        data = schema.load(request.json)
    except ValidationError as error:
        return error.messages, 400    

    query = Reservation.query

    for key, value in request.json.items():
        query = query.filter(
            getattr(Reservation, key) == value
        )

    reservations = query.all()

    schema = ReservationSchema(many=True)
    data = schema.dump(reservations)

    return jsonify(data), 200



