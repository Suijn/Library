"""A file for pytest fixtures."""
import pytest
from bookstore.main import create_app
from bookstore.extensions import db as database
import tempfile
import os
from bookstore.users.models import User, Role
import json


@pytest.fixture()
def app():
    """Create an app."""
    app = create_app()
    app.config['TESTING'] = True

    return app


@pytest.fixture()
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


@pytest.fixture(autouse=True)
def db_populate(db):
    """Populate the database with mock data."""
    
    #Create an admin user.
    admin = User("password", "admin@test.com")
    admin.roles.extend([Role('Admin'), Role('User')])

    db.session.add(admin)
    db.session.commit()

    #Create normal users.
    user = User("password", "user@test.com")
    role = Role.query.filter(Role.name=='User').one()
    user.roles.append(role)

    db.session.add(user)
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

