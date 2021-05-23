"""A module for testing the functionality of views/admins.py"""
import json
from bookstore.models import Book

def test_getBooks_OK(client, admin_access_token, db_populate_books):
    """
    Test the admin getBooks function.

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


def test_getBooks_401_Unauthorized(client, normal_access_token, db_populate_books):
    """
    Test the admin getBooks function.

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




