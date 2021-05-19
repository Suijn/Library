"""A test module for testing the functionality of the bookstore/users/views.py module."""
import json
from bookstore.users.models import User, Role


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
    assert not User.query.get(2)


def test_removeUser_404_Nonexistent_User(client, admin_access_token):
    """Test the removeUser function returns 404 when user does not exists."""
    response = client.delete(
        '/user/1000',
        headers = {
            'Authorization': 'Bearer ' + admin_access_token
        }
    )

    assert response.status_code == 404
    assert not User.query.get(1000)


def test_removeUser_401_Invalid_Token_Type(client, normal_access_token):
    """
    Test the removeUser function returns 401 if a normal access token is provided. 
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


def test_removeUser_401_No_Token(client):
    """
    Test the removeUser function returs 401 if there was no token provided.
    Assert the user is still in the database.
    """
    response = client.delete('/user/2')

    assert response.status_code == 401
    assert User.query.get(2)


def test_changeUserEmail_OK(client, normal_access_token):
    """
    Test the changeUserEmail function returns 200 and a proper json response.
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


def test_changeUserEmail_Admin_OK(client, admin_access_token):
    """
    Test the changeUserEmail function returns 200 and a proper json response
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


def test_changeUserEmail_400_Invalid_Mail(client, normal_access_token):
    """
    Test the changeUserEmail function returns 400 if an invalid user email was provided.
    
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
    """
    Test the changeUserEmail function returns 401 if user is not the owner of the account.
    
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


def test_changeUserPassword_OK(client, normal_access_token):
    """
    Test the changeUserPassword function returns 204 and no json response.
    
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


def test_changeUserPassword_401_No_Token(client):
    """
    Test the changeUserPassword function returns 401 if no token was provided.
    
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


def test_changeUserPassowrd_401_Invalid_Token(client, admin_access_token):
    """
    Test the changeUserPassword function returns 401 if token is invalid.
    
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


def test_changeUserPassword_400_Passwords_Must_Match(client, normal_access_token):
    """
    Test the changeUserPassword function returns 400 if password didn't match.
    
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


def test_changeUserPassword_401_User_Not_Owner(client, normal_access_token):
    """
    Test the changeUserPassword function returns 401 if user is not an owner of the account.
    
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


def test_changeUserPassword_400_Password_The_Same(client, normal_access_token):
    """
    Test the changeUserPassword function returns status 400 and errors, if the new password is the same as the previous one.
    
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

