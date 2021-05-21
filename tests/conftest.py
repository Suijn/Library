"""A file for pytest fixtures."""
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
    user_role = Role('User')
    admin_role = Role('Admin')

    db.session.add(user_role)
    db.session.add(admin_role)
    db.session.commit()

    #Create an admin user.
    admin = User("password", "admin@test.com")
    admin.roles.append(admin_role)

    db.session.add(admin)

    #Create normal users.
    users = [
        User("password", "user@test.com"),
        User('password', 'user2@test.com'),
        User('password', 'user3@test.com'),
        User('password', 'user4@test.com'),
        User('password', 'user5@test.com')
    ]

    db.session.add_all(users)
    db.session.commit()


@pytest.fixture()
def db_populate_books(db):
    """Populate the test database with mock books data."""

    #Create books.
    books = [
        Book('Book1', 'Author1'),
        Book('Book2', 'Author1'),
        Book('Book3', 'Author1'),
        Book('Book4', 'Author2'),
        Book('Book5', 'Author2'),
        Book('Book6', 'Author3'),
    ]
    
    db.session.add_all(books)
    db.session.commit()


@pytest.fixture()
def db_populate_reservations(db_populate_books, db):
    """Populate the mock database with test reservations data."""

    books = db.session.query(Book).all()
    users = db.session.query(User).all()


    user = User.query.filter(User.email == 'user@test.com').one()

    for x in range(5):
        res = Reservation()
        res.book = books[x]
        res.user = users[x]
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

