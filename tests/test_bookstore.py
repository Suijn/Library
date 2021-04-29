import os
import tempfile
import pytest
from bookstore.main import create_app, db as database

# from bookstore.users.models import User, RegisterSchema
import json


@pytest.fixture
def client():
    """configures the app for testing and initializes test db"""
    """creates and authenticates a user"""
    
    db, db_path = tempfile.mkstemp()
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'+ db_path

    with app.test_client() as client:
        with app.app_context():
           database.create_all()
        yield client


    email = 'admin2@email.com'
    password = 'password'
    payload = json.dumps({
        "email":email,
        "password":password,
        "password_confirmation":password
    })
    response = client.post('/register', headers={'Content-Type':'application/json'} , data=payload)

    os.close(db)
    os.unlink(db_path)


def test_empty_db(client):
    """db starts empty"""
    print()
