"""A module for testing the functionality of views/admins.py"""
import json
from tests.conftest import admin_access_token
from bookstore.models import Book


def test_get_books_ok(client, admin_access_token, db_populate_books):
    """
    Test the admin get_books function.

    :assert: response status code is 200.
    :assert: api returns a proper response.
    :assert: all books are returned in response.
    """
    response = client.get(
        'admin/books',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 200

    keys_expected = ['id','title','author','pages','isReserved']
    keys_returned = [x for x in response.json[0].keys()]

    assert set(keys_expected).issubset(set(keys_returned))
    assert len(response.json) == len(Book.query.all())    


def test_get_books_401_unauthorized(client, normal_access_token, db_populate_books):
    """
    Test the admin get_books function.

        If user is unauthorized to access this resource:
    :assert: response status code is 401.
    """
    response = client.get(
        'admin/books',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token
        }
    )

    response.status_code == 401


def test_add_book_ok(client, admin_access_token):
    """
    Test the add_book function.

    :assert: response status code is 201.
    :assert: the book was created.
    """
    payload = {
        'title': 'book1',
        'author': 'author1'
    }

    #Query the books table to get the actual state of the database.
    books = Book.query.filter(
        Book.title == 'book1',
        Book.author == 'author1'
    ).all()

    response = client.post(
        'admin/book',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 201
    assert len(books) < len(Book.query.filter(
        Book.title == 'book1',
        Book.author == 'author1'
    ).all())


def test_add_book_ok_2(client, admin_access_token):
    """
    Test the add_book function.

    :assert: response status code is 201.
    :assert: the book was created.
    """

    payload = {
        'title': 'title1',
        'author': 'author1',
        'pages': '1201'
    }

    #Query the Book table to get the actual state of the database.
    books = Book.query.filter(
        Book.title == 'title1',
        Book.author == 'author1',
        Book.pages == '1201'
    ).all()

    response = client.post(
        'admin/book',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 201
    assert len(books) < len(Book.query.filter(
        Book.title == 'title1',
        Book.author == 'author1',
        Book.pages == 1201
    ).all())


def test_add_book_400_unexpected_field(client, admin_access_token):
    """
    Test the add_book function.

    If there is an unexpected data in request:
    :assert: response status code is 400.
    :assert: book was not created.
    """
    payload = {
        'title': 'title1',
        'author': 'author1',
        'unexpectedField': "value"
    }

    #Query the Book table to get the actual state of the database.
    books = Book.query.filter(
        Book.title == 'title1',
        Book.author == 'author1'
    ).all()

    response = client.post(
        'admin/book',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert len(books) == len(Book.query.filter(
        Book.title == 'title1',
        Book.author == 'author1'
    ).all())


def test_add_book_401_unauthorized(client, normal_access_token):
    """
    Test the addBook function.

    If user is unauthorized:
    :assert: response status code is 401.
    :assert: book was not created.
    """
    payload = {
        'title': 'book1',
        'author': 'author1'
    }

    #Query the books table to get the actual state of the database.
    books = Book.query.filter(
        Book.title == 'book1',
        Book.author == 'author1'
    ).all()

    response = client.post(
        'admin/book',
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + normal_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 401
    assert len(books) == len(Book.query.filter(
        Book.title == 'book1',
        Book.author == 'author1'
    ).all())

