"""A test module to validate tests configuration."""
from bookstore.users.models import User

def test_db():
    """Test the database starts up with two users: one Admin user and one Normal user."""
    assert User.query.get(1)
    assert User.query.get(2)
    assert len(User.query.all()) == 2







    