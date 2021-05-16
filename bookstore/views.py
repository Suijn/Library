from flask import (Blueprint, jsonify, request, abort)
from .extensions import db
from .models import Book, BookSchema, BookUpdateSchema, BookSearchSchema, BookSearchSchemaAdmin, Reservation
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from .decorators import require_role
from .users.models import User
from datetime import date

blueprint = Blueprint('api', __name__, )


book_schema = BookSchema()
books_schema = BookSchema(many=True)

@blueprint.route('/books', methods=['GET'])
@jwt_required()
@require_role()
def getBooks():
    books = Book.query.all()
    payload = books_schema.dump(books)

    return jsonify(payload), 200


@blueprint.route('/book/<id>', methods=['GET'])
@jwt_required()
@require_role()
def getBook(id):
    book = Book.get_or_404(id)
    payload = book_schema.dump(book)

    return payload, 200

@blueprint.route('/books/search', methods=['POST'])
@jwt_required()
@require_role()
def searchForBooks():
    """Search for books by title and author."""
    schema = BookSearchSchema()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    
    book_title = "%{}%".format(request.json['title'])
    book_author = "%{}%".format(request.json['author'])

    books = Book.query.filter(
        Book.title.like(book_title), 
        Book.author.like(book_author)
    ).all()

    payload = books_schema.dump(books)
    return jsonify(payload), 200

@blueprint.route('/admin/books/search', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def searchForBooksAdmin():
    """Search book endpoint for admin users."""
    schema = BookSearchSchemaAdmin()

    try:
        schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400
    
    #If id is filled, then the search function returns the book with the given id.
    if request.json['id']: #Returns False if id is empty.
        book_id = int(request.json['id'])
        book = Book.get_or_404(book_id)
        payload = book_schema.dump(book)
        return payload, 200
    
    #If id is empty, then the search proceeds with the other attributes. 
    book_title = "%{}%".format(request.json['title'])
    book_author = "%{}%".format(request.json['author'])

    books = Book.query.filter(
        Book.title.like(book_title), 
        Book.author.like(book_author)
    ).all()

    payload = books_schema.dump(books)
    return jsonify(payload), 200
    

@blueprint.route('/book/<id>', methods=['DELETE'])
@jwt_required()
@require_role(['Admin'])
def deleteBook(id):
    book = Book.get_or_404(id)

    db.session.delete(book)
    db.session.commit()

    return '', 204


@blueprint.route('/book', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def addBook():
    try:
        book_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

    title = request.json['title'] 
    author = request.json['author']

    book = Book(title, author)
    
    db.session.add(book)
    db.session.commit()

    payload = book_schema.dump(book)

    return payload, 201 

@blueprint.route('/book/<id>', methods=['PATCH'])
@jwt_required()
@require_role(['Admin'])
def updateBook(id):
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


@blueprint.route('/cancelResBook/<book_id>', methods=['PATCH'])
@jwt_required()
@require_role(['Admin'])
def cancelReservation(book_id):
    """Cancel reservation of a book for the given user."""
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


@blueprint.route('/admin/reserveBook/<book_id>/<user_id>', methods=['PATCH'])
@jwt_required()
@require_role(['Admin'])
def reserveBookAsAdmin(book_id, user_id):
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





    














