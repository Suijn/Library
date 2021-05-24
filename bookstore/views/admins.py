"""A view module for admins to manage users, books and reservations."""
from flask import (Blueprint, jsonify, request, abort)
from ..models import (Book, Reservation, BookSchema, BookSearchSchemaAdmin, BookUpdateSchema)
from ..decorators import require_role
from flask_jwt_extended import jwt_required
from ..extensions import db
from marshmallow import ValidationError
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

    book = Book(title, author)
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
    Search book utility for admin users.
    
    If book_id is sent in request -- return the book with the given id.
    If book_id wasn't sent in request -- continue the search using title and author fields.
        If both title and author are filled -- search for the book with these attributes.
        If only title or author was filled -- search for the book using only the attribute that was filled.

    """
    schema = BookSearchSchemaAdmin()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    
    #If id is filled, then the search function returns the book with the given id.
    if 'id' in request.json:
        if request.json['id']:
            book_id = int(request.json['id'])
            book = Book.get_or_404(book_id)
            payload = book_schema.dump(book)
            return payload, 200
    
    #If there's no book_id in request, then the search proceeds with the other attributes. 
    if 'title' in request.json and 'author' in request.json:
        #Remove leading and trailing spaces.
        title = request.json['title'].strip()
        author = request.json['author'].strip()

        if title and author:
            #If both title and author are sent in request: 
            book_title = "%{}%".format(title)
            book_author = "%{}%".format(author)

            books = Book.query.filter(
                Book.title.like(book_title), 
                Book.author.like(book_author)
            ).all()
            payload = books_schema.dump(books)
            return jsonify(payload), 200
    if 'title' in request.json or 'author' in request.json:
        books = []
        if 'title' in request.json and not request.json['title'].isspace():
            #Remove leading and trailing spaces.
            title = request.json['title'].strip()
            books = Book.query.filter(
                Book.title.like("%{}%".format(title)), 
            ).all()
        else:
            #Remove leading and trailing spaces.
            author = request.json['author'].strip()
            books = Book.query.filter(
                Book.author.like("%{}%".format(request.json['author'])), 
            ).all()

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