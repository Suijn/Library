from flask import (Blueprint, jsonify, request, abort)
from .extensions import db
from .models import Book, BookSchema, BookUpdateSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from .decorators import require_role
from .users.models import User

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

    paylaod = book_schema.dump(book)

    return paylaod, 200


@blueprint.route('/book/<id>', methods=['DELETE'])
@jwt_required()
@require_role(['Admin'])
def deleteBook(id):
    book = Book.get_or_404(id)

    payload = book_schema.dump(book)

    db.session.delete(book)
    db.session.commit()

    return payload, 200


@blueprint.route('/book', methods=['POST'])
@jwt_required()
@require_role(['Admin'])
def addBook():
    title = request.json['title'] 
    author = request.json['author']

    try:
        book_schema.load(request.json)
    except ValidationError as err:
        return err.messages, 400

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




@blueprint.route('/reserveBook/<id>', methods=['PATCH'])
@jwt_required()
@require_role()
def reserveBook(id):
    """Reserve a book for the given user"""
    user_id = get_jwt_identity()
    book = Book.get_or_404(id)

    if book.isReserved == False or not book.user:
        book.user_id = user_id
        book.isReserved = True

        db.session.commit()

        payload = book_schema.jsonify(book)
        return payload, 200
    else:
        raise Exception('Sorry, this book is already reserved!')


@blueprint.route('/cancelResBook/<id>', methods=['PATCH'])
@jwt_required()
@require_role(['Admin'])
def cancelReservation(id):
    """Cancel reservation of a book for the given user"""
    book = Book.get_or_404(id)

    book.isReserved = False
    book.user_id = None

    db.session.commit()

    payload = book_schema.dump(book)
    return payload, 200 


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
    user = User.get_or_404(user_id)

    if book.isReserved == False and not book.user:
        book.user_id = user.id
        book.isReserved = True

        db.session.commit()
        payload = book_schema.dump(book)

        return payload, 200
    else:
        abort(500)





    














