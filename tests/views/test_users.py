"""A testing module for the views/users.py module."""
import pytest
import json
from bookstore.users.models import User
from bookstore.models import Book, Reservation
from sqlalchemy.exc import NoResultFound
from bookstore.extensions import db

class TestUsers:


    def test_get_user_reservations_ok(self, client, normal_access_token, db_populate_reservations):
        """
        Test the get_user_reservations function.

        :assert: status code is 200.
        :assert: api returns a proper response.
        :assert: user gets only his own reservations. 
        """
        user = User.query.filter(User.email == 'user@test.com').one()

        response = client.get(
            '/users/getReservations',
            headers = {
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 200
        assert response.json
        
        response_keys = [x for x in response.json[0].keys()]

        assert set(['book_id','reserved_by','expected_end_date','start_date','status','was_prolonged']).issubset(set(response_keys))
        assert response.json[0]['reserved_by'] == user.id

    
    def test_get_user_reservations_missing_token(self, client):
        """
        Test the get_user_reservations function.
            If token is missing in request:
    
        :assert: response status code is 401.
        """
        response = client.get(
            '/users/getReservations'
        )

        assert response.status_code == 401


    def test_search_for_books_all_ok(self, client, normal_access_token, db_populate_books):
        """
        Test the search_for_books function.

        :assert: status code is 200.
        :assert: api returns a proper response.
        :assert: In this test case all books in the db should be returned.
        """

        payload = {
            'title': 'book',
            'author': 'author'
        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )

        assert response.status_code == 200
        assert response.json

        response_keys = [x for x in response.json[0].keys()]

        assert set(['author','id','isReserved','pages','title']).issubset(set(response_keys))
        assert len(response.json) == len(Book.query.all())

    
    def test_search_for_books_only_title_ok(self, client, normal_access_token, db_populate_books):
        """
        Test the search_for_books function.

        :assert: status code is 200.
        :assert: api returns a proper response.
        :assert: in this test case all books should be returned.
        """

        payload = {
            'title': 'book'
        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )
        
        assert response.status_code == 200
        assert response.json

        response_keys = [x for x in response.json[0].keys()]

        assert set(['author','id','isReserved','pages','title']).issubset(set(response_keys))
        assert len(response.json) == len(Book.query.all())


    def test_search_for_books_only_author_ok(self, client, normal_access_token, db_populate_books):
        """
        Test the search_for_books function.

        :assert: status code is 200.
        :assert: api returns a proper response.
        :assert: in this test case all books should be returned.
        """

        payload = {
            'author': 'author'
        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )
        
        assert response.status_code == 200
        assert response.json

        response_keys = [x for x in response.json[0].keys()]

        assert set(['author','id','isReserved','pages','title']).issubset(set(response_keys))
        assert len(response.json) == len(Book.query.all()) 

    
    def test_search_for_books_400_both_fields_empty(self, client, normal_access_token):
        """
        Test the search_for_books function.

            If both fields are empty:
        :assert: response status code is 400.
        :assert: '_schema' error message is sent in response.
        """

        payload = {
            "title": "",
            "author":""
        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )

        assert response.status_code == 400
        assert '_schema' in response.json
        assert response.json['_schema'][0] == "No title or author."


    def test_search_for_books_400_both_fields_missing(self, client, normal_access_token):
        """
        Test the search_for_books function.

            If both fields are missing:
        :assert: response status code is 400.
        :assert: '_schema' error message is sent in response.
        """
        payload = {

        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )

        assert response.status_code == 400
        assert '_schema' in response.json
        assert response.json['_schema'][0] == "No title or author."

    
    def test_search_for_books_strip_whitespaces(self, client, normal_access_token, db_populate_books):
        """
        Test the search_for_books function.

            If in request there are leading and trailing whitespaces:
        :assert: strips leading and trailing whitespaces
        :assert: api returns a proper response.
        """

        payload = {
            "title": " book   ",
            "author":"2"
        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )

        assert response.status_code == 200
        assert response.json

        keys_expected = ['author','id','isReserved','pages','title']
        response_keys = [x for x in response.json[0].keys()]

        assert set(keys_expected).issubset(set(response_keys))

        #Strip the fields and search for books.
        book_title = "%{}%".format(payload['title'].strip())
        book_author = "%{}%".format(payload['author'].strip())
        books_expected = Book.query.filter(
            Book.title.like(book_title), 
            Book.author.like(book_author)
        ).all()

        assert len(response.json) == len(books_expected)

    
    def test_search_for_books_400_one_field_and_empty(self, client, normal_access_token):
        """
        Test the search_for_books function.

        If there is only one field filled and it is empty:
        :assert: response status code is 400.
        :assert: schema errors are sent in response.
        """
        payload = {
            "title": "",
        }
        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )
        
        assert response.status_code == 400
        assert '_schema' in response.json
        assert response.json['_schema'][0] == "No title or author."  


    def test_search_for_books_400_one_field_and_only_whitespaces(self, client, normal_access_token):
        """
        Test the search_for_books function.

        It there is only one field filled and consists of only whitespaces.
        :assert: response status code is 400.
        :assert: schema errors are sent in response.
        """
        payload = {
            "title": "      ",
        }
        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            },
            data = json.dumps(payload)
        )
        
        assert response.status_code == 400
        assert '_schema' in response.json
        assert response.json['_schema'][0] == "No title or author." 

    
    def test_search_for_books_401_token_missing(self, client):
        """
        Test the search_for_books function.

            If token is missing:
        :assert: response status code is 401.
        """
        payload = {
            'title': 'book',
            'author': 'author'
        }

        response = client.post(
            '/users/searchBooks',
            headers={
                'Content-Type':'application/json'
            },
            data = json.dumps(payload)
        )

        assert response.status_code == 401

    
    def test_get_book_OK(self, client, normal_access_token, db_populate_books):
        """
        Test the get_book function.

        :assert: response status code is 200.
        :assert: api returns a proper response.
        """
        book = Book.query.get(1)

        response = client.get(
            'users/book/' + str(book.id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer '+ normal_access_token
            }
        )

        assert response.status_code == 200
        assert response.json

        keys_expected = ['author','id','isReserved','pages','title']
        response_keys = [x for x in response.json.keys()]

        assert set(keys_expected).issubset(set(response_keys))
        assert book.id == response.json['id']

    
    def test_get_book_401_token_missing(self, client, db_populate_books):
        """
        Test the get_book function.
        
        If token is missing:
        :assert: response status code is 401.
        """
        book = Book.query.get(1)

        response = client.get(
            'users/book/' + str(book.id),
            headers = {
                'Content-Type': 'application/json'
            }
        )

        assert response.status_code == 401

    
    def test_get_book_404_book_not_exists(self, client, normal_access_token, db_populate_books):
        """
        Test the get_book function.

        If book doesn't exist:
        :assert: status code is 404
        """
        response = client.get(
            'users/book/1000',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )
        
        assert response.status_code == 404


    def test_reserve_book_ok(self, client, normal_access_token, db_populate_books):
        """
        Test the reserve_book function.

        :assert: response status code is 204.
        :assert: api returns no json response.
        :assert: reservation was created.
        """
        book = Book.query.get(1)

        response = client.post(
            'users/reserveBook/' + str(book.id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 204
        assert not response.json
        assert Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.reserved_by == User.query.filter(User.email == 'user@test.com').one().id,
            Reservation.status == 'STARTED'
        ).one()

    
    def test_reserve_book_400_book_already_reserved(self, client, normal_access_token, db_populate_reservations):
        """
        Test the reserve_book function.

        If book is already reserved:
        :assert: response status code is 400.
        :assert: reservation was not made.
        """
        book = Book.query.get(8)

        response = client.post(
            'users/reserveBook/' + str(book.id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 400
        with pytest.raises(NoResultFound):
            assert not Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.reserved_by == User.query.filter(User.email == 'user@test.com').one().id,
            Reservation.status == 'STARTED'
        ).one()


    def test_reserve_book_400_you_cannot_reserve_more_books(self, client, normal_access_token, reserve_five_books):
        """
        Test the reserve_book function.

        If user has 5 reservations with status "STARTED":
        :assert: response status code is 400.
        :assert: reservation is not created.
        """

        book = Book.query.get(6)

        response = client.post(
            'users/reserveBook/' + str(book.id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 400
        with pytest.raises(NoResultFound):
            assert not Reservation.query.filter(
            Reservation.book_id == book.id,
            Reservation.reserved_by == User.query.filter(User.email == 'user@test.com').one().id,
            Reservation.status == 'STARTED'
        ).one()


    def test_reserve_book_404_book_not_exists(self, client, normal_access_token):
        """
        Test the reserve_book function.

        If book does not exist:
        :assert: response status code is 404.
        """

        response = client.post(
            'users/reserveBook/1000',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )
        
        assert response.status_code == 404

    
    def test_reserve_book_401_missing_token(self, client, db_populate_books):
        """
        Test the reserve_book function.

        If token is missing:
        :assert: response status code is 401.
        """
        book = Book.query.get(1)
        response = client.post(
            'users/reserveBook/' + str(book.id),
            headers = {
                'Content-Type': 'application/json'
            }
        )

        assert response.status_code == 401


    def test_prolong_book_ok(self, client, normal_access_token, db_populate_reservations):
        """
        Test the prolong_book function.

        :assert: response status code is 204.
        :assert: no response json.
        :assert: reservation for the book was prolonged.  
        """
        user = User.query.filter(User.email == 'user@test.com').one()
        book_id = Reservation.query.join(User).filter(
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED'
        ).first().book_id
        

        response = client.patch(
            'users/prolongBook/' + str(book_id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 204
        assert not response.json
        assert Reservation.query.filter(
            Reservation.book_id == book_id,
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED',
            Reservation.was_prolonged == True
        ).one()


    def test_prolong_book_400_book_cannot_prolong(self, client, normal_access_token, db_populate_reservations):
        """
        Test the prolong_book function.

        If book has already been prolonged:
        :assert: response status code is 400.
        :assert: reservation wasn't prolonged.
        """
        user = User.query.filter(User.email == 'user@test.com').one()

        #Find a book that wasn't prolonged yet.
        book_id = reservation = Reservation.query.filter(
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED',
            Reservation.was_prolonged == False
        ).first().book_id
        
        # prolong the book.
        client.patch(
            'users/prolongBook/' + str(book_id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )
        
        #Try to prolong it one more time.
        
        reservation = Reservation.query.filter(
            Reservation.book_id == book_id,
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED',
            Reservation.was_prolonged == True
        ).one()
        end_date = reservation.expected_end_date

        response = client.patch(
            'users/prolongBook/' + str(book_id),
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 400
        assert end_date == Reservation.query.filter(
            Reservation.book_id == book_id,
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED',
            Reservation.was_prolonged == True
        ).one().expected_end_date


    def test_prolong_book_401_can_prolong_only_his_own_reservations(self, client, normal_access_token, db_populate_reservations):
        """
        Test the prolong_book function.
        
        If user tries to prolong a book he hasn't reserved:
        :assert: response status code is 401.
        :assert: reservation wasn't prolonged.
        """

        reservation = Reservation.query.get(1)
        end_date = reservation.expected_end_date

        response = client.patch(
            'users/prolongBook/1',
            headers = {
                'Content-Type': 'application/json',
                'Authorization': 'Bearer ' + normal_access_token
            }
        )

        assert response.status_code == 401
        assert end_date ==  Reservation.query.get(1).expected_end_date
    
    def test_prolong_book_401_token_missing(self, client, db_populate_reservations):
        """
        Test the prolong_book function.

        If token is missing:
        :assert: response status code is 401.
        :assert: reservation wasn't prolonged.
        """
        user = User.query.filter(User.email == 'user@test.com').one()
        book_id = Reservation.query.join(User).filter(
            Reservation.reserved_by == user.id,
            Reservation.status == 'STARTED',
            Reservation.was_prolonged == False
        ).first().book_id

        end_date = user.reservations[0].expected_end_date

        response = client.patch(
            'users/prolongBook/' + str(book_id),
            headers = {
                'Content-Type': 'application/json'
            }
        )

        assert response.status_code == 401
        assert end_date == Reservation.query.filter(
            Reservation.reserved_by == user.id,
            Reservation.book_id == book_id,
            Reservation.status == 'STARTED'
        ).one().expected_end_date




