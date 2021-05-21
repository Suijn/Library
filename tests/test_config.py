"""A test module to validate tests configuration."""
from bookstore.users.models import User


def test_app_config(app, db):
    """Test app configuration."""
    assert app.config['TESTING']
    assert db
    assert app.config['SQLALCHEMY_DATABASE_URI'] != 'sqlite:///db'
    assert app.secret_key == 'secret key'


def test_db(db_populate):
    """Test the database starts up with 6 users: one Admin user and 5 Normal users."""

    assert len(User.query.all()) == 6
    assert User.query.get(1).has_role('Admin')
    assert not User.query.get(2).has_role('Admin')


    







    