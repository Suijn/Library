"""A test module for testing marshmallow schemas."""
import pytest
from bookstore.users.models import RegisterSchema
from bookstore.users.models import User, Role

class TestRegisterSchema:
    """Test the register schema."""

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




