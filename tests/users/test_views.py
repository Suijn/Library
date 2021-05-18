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
    
    #Db teardown.
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


def test_getUsers_401_Invalid_Token_Type(client, normal_access_token):
    """Test the getUsers function returns 401 when a normal access token was provided."""
    response = client.get('/users', headers={'Authorization': 'Bearer ' + normal_access_token})

    assert response.status_code == 401


def test_getUsers_401_No_Token(client):
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


def test_getUser_404_User_Not_Exists(client, admin_access_token):
    """Test the getUser function returns 404 with a nonexistent user."""
    response = client.get('/user/1000', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 404


def test_getUser_401_Invalid_Token_Type(client, normal_access_token):
    """Test the getUser function returns 401 when a normal user token was provided."""
    response = client.get('/user/1', headers={'Authorization': 'Bearer ' + normal_access_token})

    assert response.status_code == 401


def test_getUser_401_No_Token(client):
    """Test the getUser function returns 401 when there was no token provided."""
    response = client.get('/user/1')

    assert response.status_code == 401


def test_removeUser_OK(client, admin_access_token):
    """Test the removeUser function returns 204 and the json response is None."""
    response = client.delete(
        '/user/2',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 204
    assert not response.json


def test_removeUser_404_Nonexistent_User(client, admin_access_token):
    """Test the removeUser function returns 404 when user does not exists."""
    response = client.delete(
        '/user/1000',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 404


def test_removeUser_401_Invalid_Token_Type(client, normal_access_token):
    """Test the removeUser function returns 401 if a normal access token is provided."""
    response = client.delete(
        '/user/2',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token
        }
    )
    assert response.status_code == 401


def test_removeUser_401_No_Token(client):
    """Test the removeUser function returs 401 if there was no token provided."""
    response = client.delete('/user/2')

    assert response.status_code == 401


def test_changeUserEmail_OK(client, normal_access_token):
    """Test the changeUserEmail function returns 200 and a proper json response."""

    payload = json.dumps({
        "email": "usermail@test.com",
    })

    response = client.patch(
        '/user/changeEmail/2',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token,
            'Content-Type':'application/json',
        },
        data=payload
    )

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert 'email' in response.json


def test_changeUserEmail_Admin_OK(client, admin_access_token):
    """
    Test the changeUserEmail function returns 200 and a proper json response
    when used by an admin.
    """
    payload = json.dumps({
        "email": "usermail@test.com",
    })

    response = client.patch(
        '/user/changeEmail/2',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token,
            'Content-Type':'application/json',
        },
        data=payload
    )

    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert 'email' in response.json


def test_changeUserEmail_400_Invalid_Mail(client, normal_access_token):
    """Test the changeUserEmail function returns 400 if an invalid user email was provided."""

    payload = json.dumps({
        "email": "usermail@.com",
    })

    response = client.patch(
        '/user/changeEmail/2',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token,
            'Content-Type':'application/json',
        },
        data=payload
    )

    assert response.status_code == 400


def test_changeUserEmail_400_Email_The_Same(client, normal_access_token):
    """Test the changeUserEmail function returns 400 if provided email was the same as the previous one."""

    payload = json.dumps({
        "email": "user@test.com",
    })

    response = client.patch(
        '/user/changeEmail/2',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token,
            'Content-Type':'application/json',
        },
        data=payload
    )

    assert response.status_code == 400


def test_changeUserEmail_401_User_Must_Be_Owner(client, normal_access_token):
    """Test the changeUserEmail function returns 401 if user is not the owner of the account."""

    payload = json.dumps({
        "email": "usermail@test.com",
    })

    response = client.patch(
        '/user/changeEmail/1',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token,
            'Content-Type':'application/json',
        },
        data=payload
    )

    assert response.status_code == 401


def test_changeUserPassword_OK(client, normal_access_token):
    """Test the changeUserPassword function returns 204 and no json response."""

    payload = json.dumps({
        "password": 'newpassword',
        "password_confirmation": 'newpassword'
    })

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token,
            'Content-Type':'application/json',
        },
        data=payload
    )
    
    assert response.status_code == 204
    assert not response.json


def test_changeUserPassword_401_No_Token(client):
    """Test the changeUserPassword function returns 401 if no token was provided."""

    payload = json.dumps({
        "password": 'newpassword',
        "password_confirmation": 'newpassword'
    })

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Content-Type':'application/json',
        },
        data=payload
    )
    
    assert response.status_code == 401


def test_changeUserPassowrd_401_Invalid_Token(client, admin_access_token):
    """Test the changeUserPassword function returns 401 if token is invalid."""

    payload = json.dumps({
        "password": 'newpassword',
        "password_confirmation": 'newpassword'
    })

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + admin_access_token,
        },
        data=payload
    )
    
    assert response.status_code == 401


def test_changeUserPassword_400_Passwords_Must_Match(client, normal_access_token):
    """Test the changeUserPassword function returns 400 if password didn't match."""

    payload = json.dumps({
        "password": 'newpassword',
        "password_confirmation": 'xyz'
    })

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + normal_access_token,
        },
        data=payload
    )
    
    assert response.status_code == 400
    assert '_schema' in response.json


def test_changeUserPassword_401_User_Not_Owner(client, normal_access_token):
    """Test the changeUserPassword function returns 401 if user is not an owner of the account."""

    payload = json.dumps({
        "password": 'newpassword',
        "password_confirmation": 'newpassword'
    })

    response = client.patch(
        '/user/changePassword/1',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + normal_access_token,
        },
        data=payload
    )
    
    assert response.status_code == 401


def test_changeUserPassword_400_Password_The_Same(client, normal_access_token):
    """Test the changeUserPassword function returns status 400 and errors, if the new password is the same as the previous one."""

    payload = json.dumps({
        "password": 'password',
        "password_confirmation": 'password'
    })

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + normal_access_token,
        },
        data=payload
    )
    
    assert response.status_code == 400
    assert '_schema' in response.json

