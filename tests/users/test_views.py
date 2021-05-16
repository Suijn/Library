import os
import tempfile
import pytest
from bookstore.main import create_app, db as database
import json

from bookstore.users.models import User, Role


@pytest.fixture
def client():
    """configures the app for testing and initializes test db."""
    
    db, db_path = tempfile.mkstemp()
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ db_path

    with app.test_client() as client:
        with app.app_context():
            #Set up db
           database.create_all()

            #Set up test admin user and a normal user.
           admin = User("password", "admin@test.com")
           admin.roles.append(Role("Admin"))
           admin.roles.append(Role("User"))
           database.session.add(admin)
           database.session.commit()

           user = User('password', 'user@test.com')

           role = Role.query.filter(Role.name=="User").one()
           user.roles.append(role)

           database.session.add(user)
           database.session.commit()

        yield client
    
    os.close(db)
    os.unlink(db_path)


@pytest.fixture
def admin_access_token(client):
    """Authenticate admin user."""

    payload = json.dumps({
        "email":"admin@test.com",
        "password":"password",
    })
    response = client.post('/login', headers={'Content-Type':'application/json'} , data=payload)
    
    access_token = response.json['access_token']
    return access_token 


@pytest.fixture
def normal_access_token(client):
    """Authenticate normal user."""
    payload = json.dumps({
        "email":"user@test.com",
        "password":"password",
    })
    response = client.post('/login', headers={'Content-Type':'application/json'} , data=payload)
    
    access_token = response.json['access_token']
    return access_token


def test_getUsers_OK(client, admin_access_token):
    """The database starts with two users in the db (One Admin user and one normal user) """
    response = client.get('/users', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 200
    assert len(response.json) == 2


def test_getUsers_401(client, normal_access_token):
    """Test the getUsers function returns 401 when a normal access token was provided."""
    response = client.get('/users', headers={'Authorization': 'Bearer ' + normal_access_token})

    assert response.status_code == 401


def test_getUsers_401_v2(client):
    """Test the getUsers function returns 401 when there was no token provided."""
    response = client.get('/users')

    assert response.status_code == 401


def test_getUser_OK(client, admin_access_token):
    """
    Test the getUser function.
    
    :assert1: asserts response status code is 200.
    :assert2: asserts the returned user has an id of 1.
    """
    response = client.get('/user/1', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 200
    assert response.json['id'] == 1


def test_getUser_404(client, admin_access_token):
    """Test the getUser function returns 404 with a nonexistent user."""
    response = client.get('/user/', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 404


def test_getUser_401(client, normal_access_token):
    """Test the getUser function returns 401 when a normal user token was provided."""
    response = client.get('/user/1', headers={'Authorization': 'Bearer ' + normal_access_token})

    assert response.status_code == 401


def test_getUser_401_2(client):
    """Test the getUser function returns 401 when there was no token provided."""
    response = client.get('/user/1')

    assert response.status_code == 401