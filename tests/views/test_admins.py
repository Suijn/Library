"""A module for testing the functionality of views/admins.py"""
import json
import re

from sqlalchemy.sql.selectable import subquery
from tests.conftest import admin_access_token
from bookstore.models import Book, BookSchema, Reservation, ReservationSchema
import pytest
from sqlalchemy.exc import NoResultFound
from bookstore.users.models import User

book_schema = BookSchema()


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


def test_update_book_ok(client, admin_access_token, db_populate_books):
    """
    Test the update_book function.

    :assert: response status code is 200.
    :assert: book was updated.
    """
    book = Book.query.get(1)

    payload = {
        "title": "updatedTitle",
        "author": "updatedAuthor",
        'pages': 111,
        'isReserved': False
    } 

    response = client.put(
        'admin/book/' + str(book.id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 200
    assert Book.query.filter(
        Book.title == payload['title'],
        Book.author == payload['author'],
        Book.pages == payload['pages'],
        Book.isReserved == payload['isReserved']
    ).one()


def test_update_book_400_field_missing_title(client, admin_access_token, db_populate_books):
    """
    Test the update_book function.

    If title is missing in request:
    :assert: response status code is 400.
    :assert: book is not updated.
    :assert: api returns a title error.
    """
    book = Book.query.get(1)

    payload = {
        "author": "updatedAuthor",
        'pages': 111,
        'isReserved': False
    } 

    response = client.put(
        'admin/book/' + str(book.id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    with pytest.raises(NoResultFound):
        assert not Book.query.filter(
            Book.author == payload['author'],
            Book.pages == payload['pages'],
            Book.isReserved == payload['isReserved']
        ).one()
    assert 'title' in response.json


def test_update_book_400_field_missing_author(client, admin_access_token, db_populate_books):
    """
    Test the update_book function.

    If author is missing in request:

    :assert: response status code is 400.
    :assert: book is not updated.
    :assert: api returns an error.
    """

    book = Book.query.get(1)

    payload = {
        'title': 'updatedTitle',
        'pages': 111,
        'isReserved': False
    } 

    response = client.put(
        'admin/book/' + str(book.id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    with pytest.raises(NoResultFound):
        assert not Book.query.filter(
            Book.title == payload['title'],
            Book.pages == payload['pages'],
            Book.isReserved == payload['isReserved']
        ).one()
    assert 'author' in response.json


def test_update_book_400_missing_required_field_pages(client, admin_access_token, db_populate_books):
    """
    Test the update_book function.

    If pages field is missing in request:

    :assert: response status code is 400.
    :assert: book is not updated.
    :assert: api returns an error.
    """
    book = Book.query.get(1)

    payload = {
        'title': 'updatedTitle',
        'author': 'updatedAuthor',
        'isReserved': False
    } 

    response = client.put(
        'admin/book/' + str(book.id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    with pytest.raises(NoResultFound):
        assert not Book.query.filter(
            Book.title == payload['title'],
            Book.author == payload['author'],
            Book.isReserved == payload['isReserved']
        ).one()
    assert 'pages' in response.json


def test_update_book_400_missing_required_field_isReserved(client, admin_access_token, db_populate_books):
    """
    Test the update_book function.

    If isReserved field is missing in request:

    :assert: response status code is 400.
    :assert: book is not updated.
    :assert: api returns an error.
    """
    book = Book.query.get(1)

    payload = {
        'title': 'updatedTitle',
        'pages': '111',
        'author': 'updatedAuthor',
    } 

    response = client.put(
        'admin/book/' + str(book.id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    with pytest.raises(NoResultFound):
        assert not Book.query.filter(
            Book.title == payload['title'],
            Book.author == payload['author'],
            Book.pages == payload['pages']
        ).one()
    assert 'isReserved' in response.json


def test_update_book_401_unauthorized(client, normal_access_token, db_populate_books):
    """
    Test the update_book function.

    If user is unauthorized:
    :assert: response status code is 401.
    :assert: book is not updated.
    """
    book = Book.query.get(1)

    payload = {
        'title': 'updatedTitle',
        'pages': '111',
        'author': 'updatedAuthor',
        'isReserved': False
    } 

    response = client.put(
        'admin/book/' + str(book.id),
        headers = {
            'Content-Type': 'application/json',
            'Authorization':'Bearer ' + normal_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 401
    with pytest.raises(NoResultFound):
        assert not Book.query.filter(
            Book.title == payload['title'],
            Book.author == payload['author'],
            Book.pages == payload['pages'],
            Book.isReserved == payload['isReserved']
        ).one()


def test_delete_book_ok(client, admin_access_token, db_populate_books):
    """
    Test the delete_book function.

    :assert: response status code is 204.
    :assert: no response json is returned.
    :assert: book was deleted.
    """

    book = Book.query.get(1)

    response = client.delete(
        'admin/book/' + str(book.id),
        headers = {
            'Authorization':'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 204
    assert not response.json
    assert not Book.query.get(1)


def test_delete_book_401_unauthorized(client, normal_access_token, db_populate_books):
    """
    Test the delete_book function.

    If user is unauthorized:
    :assert: response status code is 401.
    :assert: book wasn't deleted.
    """
    book = Book.query.get(1)

    response = client.delete(
        'admin/book/' + str(book.id),
        headers = {
            'Authorization':'Bearer ' + normal_access_token
        }
    )

    assert response.status_code == 401
    assert Book.get_or_404(1)


def test_search_for_books_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    :assert: response status code is 200.
    :assert: api returns a proper response.
    :assert: expected content was returned.
    """
    payload = {
        'id': '1',
        'title': 'book',
        'author': 'someAuthor'
    }

 
    expected_content = book_schema.dump(Book.get_or_404(payload['id']))

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 200
    content_returned = response.json
    assert expected_content == content_returned


def test_search_for_books_only_id_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    :assert: response status code is 200.
    :assert: api returns a proper response.
    """

    payload = {
        'id': '1'
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 200

    content_expected = book_schema.dump(Book.get_or_404(payload['id']))
    content_returned = response.json
    assert content_expected == content_returned


def test_search_for_books_only_title_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    :assert: response status code is 200.
    :assert: api return a proper response.
    """

    payload = {
        "title": 'book'
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 200

    content_expected = book_schema.dump(Book.query.filter(
        Book.title.like('%{}%'.format(payload['title']))
    ), many=True)

    content_returned = response.json

    assert content_expected == content_returned


def test_search_books_only_author_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    :assert: response status code is 200.
    :assert: api returns a proper response.
    """
    payload = {
        'author': 'author3'
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 200

    content_expected = book_schema.dump(Book.query.filter(
        Book.author.like('%{}%'.format(payload['author']))
    ), many=True)


    content_returned = response.json
    assert content_expected == content_returned


def test_search_for_books_400_all_fields_empty(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    If all fields are empty:
    :assert: response status code is 400.
    :assert: error message is sent in response.
    """

    data = {
        'author': '',
        'title': ''
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 400
    assert '_schema' in response.json


def test_search_for_books_400_all_fields_only_whitespaces(client, admin_access_token, db_populate_books):
    """
    Test the seach_for_books function.

    If all fields consist of only whitespaces:
    :assert: response status code is 400.
    :assert: error message is sent in response.
    """

    data = {
        "author": "        ",
        "title": " "
    }
    
    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 400
    assert '_schema' in response.json


def test_search_for_books_400_all_fields_empty_or_whitespaces(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.
    
    If all fields consist of only whitespaces or are empty:
    :assert: response status code is 400.
    :assert: error message is sent in response.
    """
    data = {
        "author": "",
        "title": "     "
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 400
    assert '_schema' in response.json


def test_search_for_books_only_id_other_empty_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    If only id is filled and the other fields are empty or consist of only whitespaces:
    :assert: response status code is 200.
    :assert: api returns proper data.
    """
    data = {
        "id": "1",
        "author": "",
        "title": "     "
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 200

    data_expected = book_schema.dump(Book.get_or_404(data['id']))
    data_returned = response.json
    assert data_expected == data_returned


def test_search_for_books_only_title_other_empty_or_spaces_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    If author field is filled and the other fields are empty or consist of only whitespaces:
    :assert: response status code is 200.
    :assert: api returns proper data.
    """
    data = {
        "author": "author",
        "title": "     "
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 200

    data_expected = book_schema.dump(Book.query.filter(
        Book.author.like("%{}%".format(data['author']))
    ).all(), many=True)

    data_returned = response.json
    assert data_expected == data_returned


def test_search_for_books_only_author_other_empty_or_spaces_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.

    If author field is filled and the other fields are empty or consist of only whitespaces:
    :assert: response status code is 200.
    :assert: api returns proper data.
    """
    data = {
        "author": "   ",
        "title": "book1"
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 200
    data_expected = book_schema.dump(Book.query.filter(
        Book.title.like("%{}%".format(data['title']))
    ).all(), many=True)
    data_returned = response.json

    assert data_expected == data_returned


def test_search_for_books_trims_spaces_ok(client, admin_access_token, db_populate_books):
    """
    Test the search_for_books function.
    
    :assert: response status code is 200.
    :assert: proper data is returned.
    """
    data = {
        "author": " 1",
        "title": "  book2  "
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + admin_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 200

    author = data['author'].strip()
    title = data['title'].strip()

    data_expected = book_schema.dump(Book.query.filter(
        Book.author.like("%{}%".format(author)),
        Book.title.like("%{}%".format(title))
    ).all(), many=True)
    data_returned = response.json

    assert data_expected == data_returned


def test_search_for_books_401_unauthorized(client, normal_access_token, db_populate_books):    
    """
    Test the search_for_books function.

    If user is unauthorized:
    :assert: response status code is 401.
    """

    data = {
        "id": "",
        "author": " 1",
        "title": "  book2  "
    }

    response = client.post(
        'admin/searchBooks',
        headers={
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + normal_access_token
        },
        data = json.dumps(data)
    )

    assert response.status_code == 401


def test_reserve_book_ok(client, admin_access_token, db_populate_books):
    """
    Test the reserve_book function.

    :assert: response status code is 204.
    :assert: no content is returned.
    :assert: reservation was created.
    """
    book = Book.get_or_404(1)
    user = User.get_or_404(1)

    response = client.post(
        f'admin/reserveBook/{book.id}/{user.id}',
        headers={
            'Authorization': f'Bearer {admin_access_token}'
        }
    )

    assert response.status_code == 204
    assert not response.json

    reservation = Reservation.query.filter(
        Reservation.book_id == book.id,
        Reservation.reserved_by == user.id,
        Reservation.status == 'STARTED'
    ).one()

    assert reservation


def test_reserve_book_401_unauthorized(client, normal_access_token, db_populate_books):
    """
    Test the reserve_book function.
    
    If user is unauthorized:
    :assert: response status code is 401.
    :assert: reservation is not created.
    """

    book = Book.get_or_404(1)
    user = User.get_or_404(1)

    response = client.post(
        f'admin/reserveBook/{book.id}/{user.id}',
        headers={
            'Authorization': f'Bearer {normal_access_token}'
        }
    )

    assert response.status_code == 401
    with pytest.raises(NoResultFound):
        reservation = Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED'
        ).one()
        assert not reservation


def test_reserve_book_400_book_already_reserved(client, admin_access_token, db_populate_books, db_populate_reservations):
    """
    Test the reserve book function.

    If book is already reserved:
    :assert: response status code is 400.
    :assert: reservation is not created.
    """

    reservation_before = Reservation.query.filter(
        Reservation.status == 'STARTED'
    ).first()

    assert reservation_before

    book = Book.get_or_404(reservation_before.book_id)
    user = User.get_or_404(1)

    response = client.post(
        f'admin/reserveBook/{book.id}/{user.id}',
        headers={
            'Authorization': f'Bearer {admin_access_token}'
        }
    )
    assert response.status_code == 400

    #Assert reservations are not changed.
    reservation_after = Reservation.query.filter(
        Reservation.book_id == book.id,
        Reservation.status == 'STARTED'
    ).one()
    assert reservation_before == reservation_after


def test_reserve_book_400_user_cannot_reserve_more_books(client,admin_access_token,reserve_five_books):
    """
    Test the reserve_book function.

    If user cannot reserve more books (user has 5 reservations with status = 'STARTED'):
    :assert: response status code is 400.
    :assert: reservation is not created.
    """
    from sqlalchemy import func

    #Get user with 5 reservations.
    user  = User.query.join(Reservation).filter(
        Reservation.status == 'STARTED'
    ).group_by(Reservation.reserved_by
    ).having(func.count(Reservation.reserved_by) == 5).one()

    #Get a book that is not reserved.
    book = Book.query.filter(
        Book.isReserved == False
    ).first()

    response = client.post(
        f'admin/reserveBook/{book.id}/{user.id}',
        headers={
            'Authorization': f'Bearer {admin_access_token}'
        }
    )
    assert response.status_code  == 400
    with pytest.raises(NoResultFound):
        reservation = Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED'
        ).one()
        assert not reservation


def test_cancel_reservation_ok(client, admin_access_token, db_populate_books, db_populate_reservations):
    """
    Test the cancel reservation function.

    :assert: response status code is 204.
    :assert: no content in response.
    :assert: reservation is cancelled.
    """
    book = Book.get_or_404(6)
    
    response = client.patch(
        f'admin/cancelResBook/{book.id}',
        headers={
            'Authorization': f'Bearer {admin_access_token}'
        }
    )

    assert response.status_code == 204
    assert not response.json

    reservation = Reservation.query.filter(
        Reservation.book_id == book.id,
        Reservation.status == "FINISHED"
    ).one()
    assert reservation

    with pytest.raises(NoResultFound):
        assert not Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.status == "STARTED"   
        ).one()


def test_cancel_reservation_401_unauthorized(client, normal_access_token, db_populate_books, db_populate_reservations):
    """
    Test the cancel reservation function.
    
    :assert: response status code is 401.
    :assert: reservation is not cancelled.
    """
    book = Book.get_or_404(6)
    
    response = client.patch(
        f'admin/cancelResBook/{book.id}',
        headers={
            'Authorization': f'Bearer {normal_access_token}'
        }
    )

    assert response.status_code == 401
    reservation = Reservation.query.filter(
        Reservation.book_id == book.id,
        Reservation.status == "STARTED"
    ).one()

    assert reservation 
    with pytest.raises(NoResultFound):
        assert not Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.status == "FINISHED"   
        ).one() 


class TestGetReservations:
    """Tests for get_reservations function."""

    @pytest.fixture(autouse=True)
    def prepare_db(self, db_populate, db_populate_reservations):
        """A fixture to prepare the test database for the tests."""


    @pytest.fixture(scope='class')
    def schema(self):
        """A fixture that returns reservations schema."""
        return ReservationSchema(many=True)


    def test_where_status(self, client, admin_access_token):
        """
        Test get_reservations function with valid data.

        :assert: api returns all reservations with status 'started'.
        """

        data = {
            'status': "STARTED"
        }

        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200
        
        schema = ReservationSchema(many=True)

        expected_data = schema.dump(
            Reservation.query.filter(
                Reservation.status == data['status']
        ).all())
        data_returned = response.json
        assert expected_data == data_returned

    
    def test_where_status_finished_and_user(self, client, admin_access_token, schema):
        """
        Test the get_reservation function with valid data.
        
        :assert: api returns all user reservations where status == 'FINISHED'.
        """
        data = {
            'reserved_by': 1,
            'status': 'FINISHED'
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200

        data_expected = schema.dump(
            Reservation.query.filter(
                Reservation.status == data['status'],
                Reservation.reserved_by == data['reserved_by']
            ).all())
            
        data_returned = response.json

        assert data_expected == data_returned


    def test_where_status_started_and_user(self, client, admin_access_token,schema):
        """
        Test the get_reservation function with valid data.
        
        :assert: api returns all user reservations where status == 'STARTED'.
        """
        data = {
            'reserved_by': 1,
            'status': 'STARTED'
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200

        data_expected = schema.dump(
            Reservation.query.filter(
                Reservation.status == data['status'],
                Reservation.reserved_by == data['reserved_by']
            ).all())
            
        data_returned = response.json

        assert data_expected == data_returned     


    def test_where_user(self, client, admin_access_token, schema):
        """
        Test the get_reservations function with valid data.

        :assert: api returns all user reservations.
        """
        data = {
            'reserved_by': 1
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200

        expected_data = schema.dump(
            Reservation.query.filter(
                Reservation.reserved_by == data['reserved_by']
        ).all())

        data_returned = response.json
        assert expected_data == data_returned

    
    def test_where_book(self, client, admin_access_token, schema):
        """
        Test the get_reservations function with valid data.

        :assert: api returns all reservations of the book.
        """
        data = {
            'book_id': 1
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200
        assert response.json

        expected_data = schema.dump(
            Reservation.query.filter(
                Reservation.book_id == data['book_id']
        ).all())

        data_returned = response.json
        assert expected_data == data_returned


    def test_where_book_user_status(self, client, admin_access_token, schema):
        """
        Test the get_reservations function with valid data.

        :assert: api returns all reservations based on the data specified in requests..
        """   

        data = {
            'reserved_by': 1,
            'book_id': 1,
            'status': 'FINISHED'
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200
        assert response.json

        expected_data = schema.dump(
            Reservation.query.filter(
                Reservation.book_id == data['book_id'],
                Reservation.reserved_by == data['reserved_by'],
                Reservation.status == data['status']
        ).all())

        data_returned = response.json
        assert expected_data == data_returned


    def test_data_leading_trailing_whitespaces(self, client, admin_access_token, schema):
        """
        Test the get_reservations function with whitespaces in data.

        :assert: api returns status code 200 and proper data.
        """
        data = {
            'reserved_by': 1,
            'book_id': 1,
            'status': '    FINISHED    '
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200
        assert response.json

        expected_data = schema.dump(
            Reservation.query.filter(
                Reservation.book_id == data['book_id'],
                Reservation.reserved_by == data['reserved_by'],
                Reservation.status == data['status'].strip()
            ).all()
        )

        data_returned = response.json
        assert expected_data == data_returned


    
    def test_user_book_as_string(self, client, admin_access_token, schema):
        """
        Test the get_reservations function with all data as strings.
        :assert: api returns status code 200 and proper data.
        """
        data = {
            'reserved_by': '1',
            'book_id': '1',
            'status': 'FINISHED'
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 200
        assert response.json
        
        expected_data = schema.dump(
            Reservation.query.filter(
                Reservation.book_id == data['book_id'],
                Reservation.reserved_by == data['reserved_by'],
                Reservation.status == data['status']
            ).all()
        )
        assert expected_data == response.json

    
    def test_missing_required_data(self, client, admin_access_token):
        """
        Test the get_reservations function with missing data.

        :assert: schema raises validation error if there's no data in request.
        """
        data = {

        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )

        assert response.status_code == 400
        assert '_schema' in response.json
        assert 'No status, user or book.' in response.json['_schema'] 


    def test_missing_data_only_whitespaces(self, client, admin_access_token):
        """
        Test the get_reservations function with only whitespaces in data.
        

        :assert: response status code is 400.
        :assert: api returns errors in response.
        """
        data = {
            'reserved_by': ' ',
            'book_id': ' ',
            'status': '    '
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 400
        assert 'Not a valid integer.' in response.json['book_id']
        assert 'Not a valid integer.' in response.json['reserved_by']


    
    def test_missing_data_all_fields_empty(self, client, admin_access_token):
        """
        Test the get_reservations function with invalid data (reserved_by, book_id)
        -- integer expected or a string that can be converted to integer.

        :assert: response status code is 400.
        :assert: api returns errors in response.
        """
        data = {
            'reserved_by': '',
            'book_id': '',
            'status': 'FINISHED'
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 400
        assert 'Not a valid integer.' in response.json['book_id']
        assert 'Not a valid integer.' in response.json['reserved_by']
        

    def test_missing_data_only_status_and_empty(self, client, admin_access_token):
        """
        Test the get_reservations function with invalid data.
        :assert: response status code is 400.
        :assert: errors are sent in response.
        """
        data = {
            'status': ''
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {admin_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 400
        assert '_schema' in response.json


    def test_unauthorized(self, client, normal_access_token, schema):
        """
        Test the get_reservations function with valid data but invalid access token.

        :assert: api returns status code 401 and data is not returned.
        """
        data = {
            'status': 'FINISHED'
        }
        response = client.post(
            'admin/getReservations',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {normal_access_token}'
            },
            data = json.dumps(data)
        )
        assert response.status_code == 401
        assert not response.json

