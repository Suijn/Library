"""A test module for testing the functionality of the bookstore/users/views.py module."""
import pytest
import json
from marshmallow.fields import Email
from bookstore.users.models import User, Role
from sqlalchemy.exc import NoResultFound
from flask import request
from flask_jwt_extended import create_refresh_token
from datetime import timedelta
import time

def test_get_users_ok(client, admin_access_token):
    """The database starts with 6 users in the db (One Admin user and 5 normal users) """
    response = client.get('/users', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 200
    assert len(response.json) == 6


def test_get_users_401_invalid_token_type(client, normal_access_token):
    """Test the get_users function returns 401 when a normal access token was provided."""
    response = client.get('/users', headers={'Authorization': 'Bearer ' + normal_access_token})

    assert response.status_code == 401


def test_get_users_401_no_token(client):
    """Test the get_users function returns 401 when there was no token provided."""
    response = client.get('/users')

    assert response.status_code == 401


def test_get_user_OK(client, admin_access_token):
    """
    Test the get_user function.
    
    :assert1: asserts response status code is 200.
    :assert2: asserts the returned user has an id of 1.
    """
    response = client.get('/user/1', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 200
    assert response.json['id'] == 1


def test_get_user_404_user_not_exists(client, admin_access_token):
    """Test the get_user function returns 404 with a nonexistent user."""
    response = client.get('/user/1000', headers={'Authorization': 'Bearer ' + admin_access_token})

    assert response.status_code == 404


def test_get_user_401_invalid_token_type(client, normal_access_token):
    """Test the get_user function returns 401 when a normal user token was provided."""
    response = client.get('/user/1', headers={'Authorization': 'Bearer ' + normal_access_token})

    assert response.status_code == 401


def test_get_user_401_no_token(client):
    """Test the get_user function returns 401 when there was no token provided."""
    response = client.get('/user/1')

    assert response.status_code == 401


def test_remove_user_ok(client, admin_access_token):
    """Test the remove_user function returns 204 and the json response is None."""
    response = client.delete(
        '/user/2',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 204
    assert not response.json
    assert not User.query.get(2)


def test_remove_user_404_nonexistent_user(client, admin_access_token):
    """Test the remove_user function returns 404 when user does not exists."""
    response = client.delete(
        '/user/1000',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 404
    assert not User.query.get(1000)


def test_remove_user_401_invalid_token_type(client, normal_access_token):
    """
    Test the remove_user function returns 401 if a normal access token is provided. 
    Assert the user is still in the database.
    """
    response = client.delete(
        '/user/2',
        headers = {
            'Authorization': 'Bearer ' + normal_access_token
        }
    )

    assert response.status_code == 401
    assert User.query.get(2)


def test_remove_user_401_no_token(client):
    """
    Test the remove_user function returs 401 if there was no token provided.
    Assert the user is still in the database.
    """
    response = client.delete('/user/2')

    assert response.status_code == 401
    assert User.query.get(2)


def test_change_user_email_ok(client, normal_access_token):
    """
    Test the change_user_email function returns 200 and a proper json response.
    Assert returned email address is the same as payload.
    """

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
    assert response.json['email'] == 'usermail@test.com'


def test_change_user_email_admin_ok(client, admin_access_token):
    """
    Test the change_user_email function returns 200 and a proper json response
    when used by an admin.

    :assert: the returned email address is the same as email in the payload.
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
    assert response.json['email'] == 'usermail@test.com'


def test_change_user_email_400_invalid_mail(client, normal_access_token):
    """
    Test the change_user_email function returns 400 if an invalid user email was provided.
    
    :assert: Email was not changed.
    """

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
    assert User.query.get(2).email != "usermail@.com"


def test_change_user_email_400_email_the_same(client, normal_access_token):
    """Test the change_user_email function returns 400 if provided email was the same as the previous one."""

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


def test_change_user_email_401_user_must_be_owner(client, normal_access_token):
    """
    Test the change_user_email function returns 401 if user is not the owner of the account.
    
    :assert" Email was not changed.
    """

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
    assert User.query.get(1).email != "usermail@test.com"


def test_change_user_password_ok(client, normal_access_token):
    """
    Test the change_user_password function returns 204 and no json response.
    
    :assert: Password was changed.
    """

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
    assert User.query.get(2).check_password('newpassword')


def test_change_user_password_401_no_token(client):
    """
    Test the change_user_password function returns 401 if no token was provided.
    
    :assert: Password was not changed.
    """

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
    assert not User.query.get(2).check_password('newpassword')


def test_change_user_passowrd_401_invalid_token(client, admin_access_token):
    """
    Test the change_user_password function returns 401 if token is invalid.
    
    :assert: Password was not changed.
    """

    payload = {
        "password": 'newpassword',
        "password_confirmation": 'newpassword'
    }

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + admin_access_token,
        },
        data=json.dumps(payload)
    )
    
    assert response.status_code == 401
    assert not User.query.get(2).check_password(payload['password'])


def test_change_user_password_400_passwords_must_match(client, normal_access_token):
    """
    Test the change_user_password function returns 400 if password didn't match.
    
    :assert: json response returns errors.
    :assert: password was not changed.
    """

    payload = {
        "password": 'newpassword',
        "password_confirmation": 'xyz'
    }

    response = client.patch(
        '/user/changePassword/2',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + normal_access_token,
        },
        data=json.dumps(payload)
    )
    
    assert response.status_code == 400
    assert '_schema' in response.json
    assert not User.query.get(2).check_password(payload['password'])


def test_change_user_password_401_user_not_owner(client, normal_access_token):
    """
    Test the change_user_password function returns 401 if user is not an owner of the account.
    
    :assert: Password was not changed.
    """

    payload ={
        "password": 'newpassword',
        "password_confirmation": 'newpassword'
    }

    response = client.patch(
        '/user/changePassword/1',
        headers = {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + normal_access_token,
        },
        data=json.dumps(payload)
    )
    
    assert response.status_code == 401
    assert not User.query.get(1).check_password(payload['password'])


def test_change_user_password_400_password_the_same(client, normal_access_token):
    """
    Test the change_user_password function returns status 400 and errors, if the new password is the same as the previous one.
    
    :assert: response status code is 400.
    :assert: errors were returned in response.
    """

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


def test_register_user_ok(client):
    """
    Test the register_user function.
    
    :assert: status code is 201.
    :assert: user was returned in response.
    :assert: user has a role "User" and doesn't have a role "Admin".
    :assert: user is in the database.
    :assert: a new user is created with 0 books reserved.
    """
    payload = {
        "email": "newuser@test.com",
        "password": 'password',
        "password_confirmation": 'password'
    }

    response = client.post(
        '/register',
        headers = {
            'Content-Type':'application/json'
        },
        data=json.dumps(payload)
    )

    user = User.query.filter(User.email == payload['email']).one()

    assert response.status_code == 201
    assert response.json
    assert 'email' in response.json
    assert payload['email'] == response.json['email']
    assert user
    assert user.has_role("User")
    assert not user.has_role("Admin")
    assert user.books_amount == 0


def test_registerUser_400_email_already_exists(client):
    """
    Test the register_user function.

    :assert: response status code is 400.
    :assert: error 'email' is returned in response.
    :assert: there is only one user with this email in the database.
    """
    payload = {
        "email": User.get_or_404(1).email,
        "password": 'password',
        "password_confirmation": 'password'
    }

    response = client.post(
        '/register',
        headers = {
            'Content-Type':'application/json'
        },
        data=json.dumps(payload)
    )

    assert response.status_code == 400
    assert 'email' in response.json
    assert len(User.query.filter(User.email == payload['email']).all()) == 1


def test_register_user_400_passwords_must_match(client):
    """
    Test the register_user function.
        
        If password don't match
    :assert: status code is 400.
    :assert: _schema is included in response.
    :assert: user was not registered.
    """
    payload = {
        "email": 'newuser@test.com',
        "password": 'password',
        "password_confirmation": 'password1'
    }

    response = client.post(
        '/register',
        headers = {
            'Content-Type':'application/json'
        },
        data=json.dumps(payload)
    )

    assert response.status_code == 400
    assert '_schema' in response.json
    with pytest.raises(NoResultFound):
        assert not User.query.filter(User.email == payload['email']).one()


def test_register_user_400_invalid_email(client):
    """
    Test the register_user function.

        If provided email address was invalid:
    :assert: response status code is 400.
    :assert: email errors are returned in response
    :assert: user was not registered.
    """
    payload = {
        "email": 'invalidmail@.com',
        "password": 'password',
        "password_confirmation": 'password'
    }

    response = client.post(
        '/register',
        headers = {
            'Content-Type':'application/json'
        },
        data=json.dumps(payload)
    )

    assert response.status_code == 400
    assert 'email' in response.json
    with pytest.raises(NoResultFound):
        assert not User.query.filter(User.email == payload['email']).one()


def test_register_user_400_email_missing(client):
    """
    Test the register_user function.

        If email is missing:
    :assert: response status code is 400.
    :assert: email errors are in response json.
    """
    payload = {
        "password": 'password',
        "password_confirmation": 'password'
    }

    response = client.post(
        '/register',
        headers = {
            'Content-Type':'application/json'
        },
        data=json.dumps(payload)
    )

    assert response.status_code == 400
    assert 'email' in response.json


def test_register_user_400_password_missing(client):
    """
    Test the register_user function.

        If password is missing:
    :assert: response status code is 400.
    :assert: password errors are in response json.
    :assert: user was not registered.
    """
    payload = {
        "email": 'test10@user.com',
        "password_confirmation": 'password'
    }

    response = client.post(
        '/register',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert 'password' in response.json
    with pytest.raises(NoResultFound):
        assert not User.query.filter(User.email == payload['email']).one()


def test_register_user_400_password_confirmation_missing(client):
    """
    Test the register_user function.

        If password_confirmation is missing:
    :assert: response status code is 400.
    :assert: password_confirmation errors are in response.
    :assert: user was not created.
    """

    payload = {
        "email": 'test10@user.com',
        'password': 'password'
    }

    response = client.post(
        '/register',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert 'password_confirmation' in response.json
    with pytest.raises(NoResultFound):
        assert not User.query.filter(User.email == payload['email']).one()


def test_login_ok(client):
    """
    Test the login function.

    :assert: response status code is 200.
    :assert: access token is in response.
    :assert: refresh token is in response.
    """
    payload = {
        "email": User.get_or_404(2).email,
        "password": "password"
    }

    response = client.post(
        '/login',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 200
    assert 'access_token' in response.json
    assert 'refresh_token' in response.json


def test_login_400_invalid_email(client):
    """
    Test the login function.

        If email address is invalid
    :assert: response status code is 400.
    :assert: no token is sent.
    :assert: _schema error message is in response.
    """
    payload = {
        "email": 'invalid@test.com',
        "password": "password"
    }

    response = client.post(
        '/login',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert not 'access_token' in response.json
    assert not 'refresh_token' in response.json
    assert '_schema' in response.json
    assert 'Wrong credentials!' in response.json['_schema']


def test_login_400_invalid_password(client):
    """
    Test the login function.

        If password is invalid:
    :assert: response status code is 400.
    :assert: No token is sent in response.
    :assert: _schema error message is sent in response.
    """
    payload = {
        "email": User.get_or_404(2).email,
        "password": "invalidpassword"
    }

    response = client.post(
        '/login',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert not 'access_token' in response.json
    assert not 'refresh_token' in response.json
    assert '_schema' in response.json
    assert 'Wrong credentials!' in response.json['_schema']


def test_login_400_email_missing(client):
    """
    Test the login function.

        If email is missing:
    :assert: response status is 400.
    :assert: No token is sent in response.
    :assert: email error is sent in response.
    """
    payload = {
        "password": "invalidpassword"
    }

    response = client.post(
        '/login',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert not 'access_token' in response.json
    assert not 'refresh_token' in response.json
    assert 'email' in response.json


def test_login_400_password_missing(client):
    """
    Test the login function.

        If password is missing:
    :assert: response status code is 400.
    :assert: no token is sent in response.
    :assert: password error message in sent in response.
    """

    payload = {
        "email": User.get_or_404(2).email
    }

    response = client.post(
        '/login',
        headers= {
            'Content-Type':'application/json'
        },
        data = json.dumps(payload)
    )

    assert response.status_code == 400
    assert not 'access_token' in response.json
    assert not 'refresh_token' in response.json
    assert 'password' in response.json


def test_refresh_token_ok(client, refresh_token):
    """
    Test the refresh_token function.

        If refresh token is sent in request.
    :assert: response status code is 200.
    :assert: access token is sent in response.
    """

    response = client.post(
        '/refreshToken',
        headers= {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + refresh_token
        }
    )

    assert response.status_code == 200
    assert 'access_token' in response.json


def test_refresh_token_401_missing_refresh_token(client):
    """
    Test the refresh_token function.

        If refresh token is missing in request:
    :assert: response status code is 401.
    :assert: the new access token is not sent.
    """
    response = client.post(
        '/refreshToken',
        headers= {
            'Content-Type':'application/json'
        }
    )

    assert response.status_code == 401
    assert not 'access_token' in response.json


def test_refresh_token_400_invalid_refresh_token(client, refresh_token):
    """
    Test the refresh_token function.

        If refresh token is invalid:
    :assert: response status code is 422.
    :assert: the new access token is not sent in response.
    :assert: error message is sent in response.
    """

    response = client.post(
        '/refreshToken',
        headers= {
            'Content-Type':'application/json',
            'Authorization': 'Bearer ' + refresh_token + '12351kasdmasj'
        }
    )

    assert response.status_code == 422
    assert not 'access_token' in response.json
    assert 'msg' in response.json


