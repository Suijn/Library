from flask import (Blueprint, jsonify, request)
from .extensions import db
from .models import Book, BookSchema
from flask_jwt_extended import jwt_required
from marshmallow import ValidationError

blueprint = Blueprint('api', __name__, )


book_schema = BookSchema()
books_schema = BookSchema(many=True)

@blueprint.route('/books', methods=['GET'])
@jwt_required()
def getBooks():
    books = Book.query.all()

    payload = books_schema.dump(books)

    return jsonify(payload), 200


@blueprint.route('/book/<id>', methods=['GET'])
@jwt_required()
def getBook(id):
    book = Book.query.get(id)

    paylaod = book_schema.dump(book)

    return paylaod, 200


@blueprint.route('/book/<id>', methods=['DELETE'])
@jwt_required()
def deleteBook(id):
    book = Book.query.get(id)

    if not book:
        raise Exception('An Error happened during removing the book!')

    payload = book_schema.dump(book)

    db.session.delete(book)
    db.session.commit()

    return payload, 200


@blueprint.route('/book', methods=['POST'])
@jwt_required()
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


@blueprint.route('/book/<id>', methods=['PUT'])
@jwt_required()
def updateBook(id):
    book = Book.query.get(id)

    title = request.json['title']
    author = request.json['author']
    pages = request.json['pages']

    book.title = title
    book.author = author
    book.pages = pages

    db.session.commit()

    payload = book_schema.jsonify(book)
    return payload, 200







