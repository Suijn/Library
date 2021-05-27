"""A test module for testing marshmallow schemas."""
from os import error
import pytest
from bookstore.users.models import LoginSchema, RegisterSchema, UpdatePasswordSchema
from bookstore.users.models import User, Role
from bookstore.extensions import db


class TestRegisterSchema:
    """Test register schema."""

    @pytest.fixture(scope='class')
    def schema(self):
        """Return schema."""
        return RegisterSchema()
    

    def test_validates_ok(self, schema):
        """Assert schema validation raises no errors if data is correct."""
        data = {
            'email': 'test@email.com',
            'password': 'password',
            'password_confirmation': "password"
        }

        errors = schema.validate(data)
        assert not errors

    
    def test_validate_missing_email(self, schema):
        """Assert schema raises errors if email is missing."""

        data = {
            'password': 'password',
            'password_confirmation': "password"
        }

        errors = schema.validate(data)
        assert errors
        assert errors['email']

    
    def test_validate_missing_password(self, schema):
        """Assert schema raises errors if password is missing."""

        data = {
            'email': 'test@email.com',
            'password_confirmation': "password"
        }

        errors = schema.validate(data)
        assert errors
        assert errors['password']


    def test_validate_missing_password_confirmation(self, schema):
        """Assert schema raises errors if password_confirmation is missing."""

        data = {
            'email': 'test@email.com',
            'password': 'password',
        }

        errors = schema.validate(data)
        assert errors
        assert errors['password_confirmation'] 

    
    def test_unknown_field(self, schema):
        """Assert schema raises errors if unexpected field is sent in request."""

        data = {
            'email': 'test@email.com',
            'password': 'password',
            'password_confirmation': "password",
            'some_field':'some_value'
        }

        errors = schema.validate(data)
        assert errors
        assert errors['some_field']

  
    def test_password_not_match(self, schema):
        """Assert schema validation raises ValidationError if passwords are not the same."""

        data = {
            'email': 'test@email.com',
            'password': 'password',
            'password_confirmation': "sdasfs"
        }

        errors = schema.validate(data)
        assert errors
        assert errors['_schema']

    
    def test_email_unique(self, schema, db_populate):
        """Assert schema raises errors if email is not unique."""
        user_email = User.get_or_404(1).email

        data = {
            'email': f'{user_email}',
            'password': 'password',
            'password_confirmation': "password"
        }
        
        errors = schema.validate(data)
        assert errors
        assert errors['email']


class TestLoginSchema:
    """Test login schema."""


    @pytest.fixture(autouse=True)
    def set_up(self, db_populate):
        """
        A fixture to call db_populate fixture automatically on every test function in this class.
        """


    @pytest.fixture(scope='class')
    def schema(self):
        """Return schema."""
        return LoginSchema()

    
    def test_validation_ok(self, schema):
        """
        Test schema with valid data.
        
        :assert: schema returns no errors.
        """

        data = {
            'email': 'user@test.com',
            'password': 'password'
        }
        errors = schema.validate(data)
        assert not errors

    
    def test_validation_incorrect_email(self, schema):
        """
        Test incorrect email against schema validation.
        """

        data = {
            'email': 'very@incorrect_email.com',
            'password': 'password'
        }

        errors = schema.validate(data)
        assert errors
        assert 'email' in errors

    
    def test_validation_wrong_credentials(self, schema):
        """
        Test incorrect login credentials against schema validation.
        """
        data = {
            'email': 'user@test50.com',
            'password': 'password'
        }

        errors = schema.validate(data)
        assert errors
        assert '_schema' in errors

    
    def test_validation_wrong_credentials_2(self, schema):
        """
        Test incorrect data against schema validation.
        """
        data = {
            'email': 'user@test.com',
            'password': 'incorrectpassword'
        }

        errors = schema.validate(data)
        assert errors
        assert '_schema' in errors


class TestUpdatePasswordSchema:
    """Test update password schema."""


    @pytest.fixture(autouse=True)
    def set_up(self, db_populate):
        """
        A set up fixture to call db_populate on every test function of this class.
        """
    
    @pytest.fixture()
    def schema(self, app):
        """
        Create a mock user and pass it to the schema. 
        Return UpdatePasswordSchema.
        """
        user = User(password='password', email='test@email.com')

        return UpdatePasswordSchema(user=user)


    def test_validate_ok(self, schema):
        """Test schema with correct data."""

        data = {
            'password':'newpassword',
            'password_confirmation': 'newpassword'
        }

        errors = schema.validate(data)
        assert not errors

    
    def test_validate_password_must_match(self, schema):
        """
        Assert schema raises validation error when passwords don't match.
        """

        data = {
            'password':'newpassword',
            'password_confirmation': 'somedifferentpassword'
        }

        errors = schema.validate(data)
        assert errors
        assert errors['_schema']
        assert errors['_schema'][0] == 'Passwords must match'


    def test_validate_password_is_different(self, schema):
        """
        If the new password is the same as the previous one:
        :assert: schema raises validation error.
        """

        data = {
            'password': 'password',
            'password_confirmation': 'password'
        }

        errors = schema.validate(data)
        assert errors
        assert errors['_schema']
        assert errors['_schema'][0] == "Password must be different from the previous one."