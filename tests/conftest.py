"""A file for pytest fixtures."""
from _pytest.capture import TeeCaptureIO
from werkzeug.exceptions import TooManyRequests
from bookstore.models import Reservation, ReservationSchema
import pytest
from bookstore.main import create_app
from bookstore.extensions import db as database
import tempfile
import os
from bookstore.users.models import User, Role
from bookstore.models import Book, Reservation
import json


@pytest.fixture()
def app():
    """Create an app."""
    app = create_app()
    app.config['TESTING'] = True

    return app


@pytest.fixture(autouse=True)
def db(app):
    """Yield db and tear it down."""
    db, db_path = tempfile.mkstemp()
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ db_path
    
    with app.app_context():
        database.create_all()
        yield database

    #Database teardown.
    os.close(db)
    os.unlink(db_path)


@pytest.fixture()
def db_populate(db):
    """Populate the database with mock user data."""
    
    #Create roles
    user_role = Role(name='User')
    admin_role = Role(name='Admin')

    db.session.add(user_role)
    db.session.add(admin_role)
    db.session.commit()

    #Create an admin user.
    admin = User(password="password", email="admin@test.com")
    admin.roles.append(admin_role)

    db.session.add(admin)

    #Create normal users.
    users = [
        User(password="password", email="user@test.com"),
        User(password='password', email='user2@test.com'),
        User(password='password', email='user3@test.com'),
        User(password='password', email='user4@test.com'),
        User(password='password', email='user5@test.com')
    ]

    db.session.add_all(users)
    db.session.commit()


@pytest.fixture()
def db_populate_books(db):
    """Populate the test database with mock books data."""
    books = []

    for x in range(20):
        books.append(
            Book(title=f'Book{x}', author=f'Author{x}')
        )
    
    db.session.add_all(books)
    db.session.commit()


@pytest.fixture()
def db_populate_reservations(db_populate_books, db):
    """Populate the mock database with reservations data."""

    books = db.session.query(Book).all()
    users = db.session.query(User).all()

    for x in range(len(users)):
        res = Reservation()
        res.book = books[x]
        res.user = users[x]

        books[x].isReserved = True
        users[x].books_amount += 1

        db.session.add(res)
    db.session.commit()
    
    #Make some additional reservations.
    res1 = Reservation()
    res1.user = users[1]
    res1.book = books[6]
    books[6].isReserved = True
    db.session.add(res1)

    res2 = Reservation()
    res2.user = users[0]
    res2.book = books[7]
    books[7].isReserved = True
    db.session.add(res2)

    res3 = Reservation()
    res3.user = users[2]
    res3.book = books[8]
    books[8].isReserved = True
    db.session.add(res3)

    res4 = Reservation()
    res4.user = users[3]
    res4.book = books[9]
    books[9].isReserved = True
    db.session.add(res4)
    
    res5 = Reservation()
    res5.user = users[4]
    res5.book = books[9]
    books[9].isReserved = True
    db.session.add(res5)

    db.session.commit()

    #Mark some reservations as 'Finished'.
    for x in range(1,5):
        res = Reservation.query.get(x)
        res.status='FINISHED'
        book = Book.get_or_404(res.reserved_by)
        book.isReserved = False
    
    db.session.commit()


@pytest.fixture()
def reserve_five_books(db,db_populate, db_populate_books):
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


@pytest.fixture()
def client(app, db_populate):
    with app.test_client() as client:
        yield client


@pytest.fixture()
def admin_access_token(client):
    """Authenticate admin user."""

    payload = json.dumps({
        "email":"admin@test.com",
        "password":"password",
    })
    response = client.post('/login', headers={'Content-Type':'application/json'} , data=payload)
    
    access_token = response.json['access_token']
    return access_token 


@pytest.fixture()
def normal_access_token(client):
    """Authenticate normal user."""

    payload = json.dumps({
        "email":"user@test.com",
        "password":"password",
    })
    response = client.post('/login', headers={'Content-Type':'application/json'} , data=payload)
    
    access_token = response.json['access_token']
    return access_token


@pytest.fixture()
def refresh_token(client):
    """Get the refresh token."""
    payload = json.dumps({
        "email":"admin@test.com",
        "password":"password",
    })

    response = client.post('/login', headers={'Content-Type':'application/json'} , data=payload)
    
    refresh_token = response.json['refresh_token']
    return refresh_token


@pytest.fixture()
def cli_runner(app, db_populate):
    runner = app.test_cli_runner()

    return runner

