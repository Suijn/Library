"""A testing module for the views/users.py module."""
import pytest
import json
from bookstore.users.models import User
from bookstore.models import Book, Reservation
from sqlalchemy.exc import NoResultFound
from bookstore.extensions import db

class TestUsers:

    @pytest.fixture()
    def reserveFiveBooks(self, db_populate, db_populate_books):
        """
        Populates the test database with 5 reservations created for one single user.
        """

        books = db.session.query(Book).all()
        user = db.session.query(User).filter(User.email == 'user@test.com').one()

        for x in range(5):
            res = Reservation()
            res.book = books[x]
            res.user = user

            books[x].isReserved = True
            user.books_amount += 1

            db.session.add(res)
        db.session.commit()


    def test_getUserReservations_OK(self, client, normal_access_token, db_populate_reservations):
        """
        Test the getUserReservations function.

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

    
    def test_getUserReservations_Missing_Token(self, client):
        """
        Test the getUserReservation function.
            If token is missing in request:
    
        :assert: response status code is 401.
        """
        response = client.get(
            '/users/getReservations'
        )

        assert response.status_code == 401


    def test_searchForBooks_All_OK(self, client, normal_access_token, db_populate_books):
        """
        Test the searchForBooks function.

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

    
    def test_searchForBooks_Only_Title_OK(self, client, normal_access_token, db_populate_books):
        """
        Test the searchForBooks function.

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


    def test_searchForBooks_Only_Author_OK(self, client, normal_access_token, db_populate_books):
        """
        Test the searchForBooks function.

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

    
    def test_searchForBooks_400_Both_Fields_Empty(self, client, normal_access_token):
        """
        Test the searchForBooks function.

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


    def test_searchForBooks_400_Both_Fields_Missing(self, client, normal_access_token):
        """
        Test the searchForBooks function.

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

    
    def test_searchForBooks_Strip_Whitespaces(self, client, normal_access_token, db_populate_books):
        """
        Test the searchForBooks function.

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

    
    def test_searchForBooks_400_One_Field_AND_Empty(self, client, normal_access_token):
        """
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


    def test_searchForBooks_400_One_Field_AND_Only_Whitespaces(self, client, normal_access_token):
        """
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

    
    def test_searchForBooks_401_Token_Missing(self, client):
        """
        Test the searchForBooks function.

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

    
    def test_getBook_OK(self, client, normal_access_token, db_populate_books):
        """
        Test the getBook function.

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

    
    def test_getBook_401_Token_Missing(self, client, db_populate_books):
        """
        Test the getBook function.
        
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

    
    def test_getBook_404_Book_Not_Exists(self, client, normal_access_token, db_populate_books):
        """
        Test the getBook function.

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


    def test_reserveBook_OK(self, client, normal_access_token, db_populate_books):
        """
        Test the reserveBook function.

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

    
    def test_reserveBook_400_Book_Already_Reserved(self, client, normal_access_token, db_populate_reservations):
        """
        Test the reserveBook function.

        If book is already reserved:
        :assert: response status code is 400.
        :assert: reservation was not made.
        """
        book = Book.query.get(3)

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


    def test_reserveBook_400_You_Cannot_Reserve_More_Books(self, client, normal_access_token, reserveFiveBooks):
        """
        Test the reserveBook function.

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


    def test_reserveBook_404_Book_Not_Exists(self, client, normal_access_token):
        """
        Test the reserveBook function.

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

    
    def test_reserveBook_401_Missing_Token(self, client, db_populate_books):
        """
        Test the reserveBook function.

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







