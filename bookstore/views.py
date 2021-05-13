from flask import (Blueprint, jsonify, request)
from .extensions import db
from .models import Book, BookSchema
from flask_jwt_extended import jwt_required, get_jwt_identity
from marshmallow import ValidationError
from .decorators import require_role

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





@blueprint.route('/registerBook/<id>', methods=['PATCH'])
@jwt_required()
@require_role()
def registerBook(id):
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




    














