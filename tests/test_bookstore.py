import os
import tempfile
import pytest
from bookstore.main import create_app, db as database
import json


@pytest.fixture
def client():
    """configures the app for testing and initializes test db"""
    
    db, db_path = tempfile.mkstemp()
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ db_path

    with app.test_client() as client:
        with app.app_context():
           database.create_all()
        yield client
    
    os.close(db)
    os.unlink(db_path)


@pytest.fixture
def access_token(client):
    """creates and authenticates a test user"""

    email = 'admin2@email.com'
    password = 'password'
    payload = json.dumps({
        "email":email,
        "password":password,
        "password_confirmation":password
    })

    response = client.post('/register', headers={'Content-Type':'application/json'} , data=payload)

    payload = json.dumps({
        "email":email,
        "password":password,
    })
    response = client.post('/login', headers={'Content-Type':'application/json'} , data=payload)
    
    access_token = response.json['access_token']
    return access_token 


def test_db(client, access_token):
    """db starts with one user in db"""
    response = client.get('/users', headers={'Authorization': 'Bearer ' + access_token})
    
    assert response.status_code == 200
    assert len(response.json) == 1