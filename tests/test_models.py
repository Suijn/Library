"""Model unit tests."""
from re import T
from bookstore.users.models import User, Role, roles_users
from bookstore.models import Book, Reservation
from bookstore.extensions import db

class TestUser:
    """User tests."""


    def test_get_or_404_ok(self, db_populate):
        """Get user by ID."""
        user = User('password', 'email@test.com')
        db.session.add(user)
        db.session.commit()

        retrieved = User.get_or_404(user.id)
        assert retrieved == user

    
    def test_default_fields(self, db_populate):
        """Test the default fields."""
        user = User.get_or_404(3)

        assert user.books_amount == 0
        assert user.has_role('User')

    
    def test_check_password(self, db_populate):
        """Test that check_password method works properly."""
        user = User('password', 'email@test.com')

        assert user.check_password('password') is True
        assert user.check_password('bawrsdfa') is False 


    def  test_has_role(self, db_populate):
        """Test the has_role method."""
        user = User.get_or_404(1)

        assert user.has_role('User') is True

    
    def test_has_roles(self, db_populate):
        """Test the has_roles method."""
        admin_role = Role.query.filter(Role.name == 'Admin').one()

        #Get normal user.
        subquery = db.session.query(roles_users).filter(
            roles_users.c.user_id == User.id,
            roles_users.c.role_id == admin_role.id
        )
        normal_user = User.query.filter(
            ~subquery.exists()
        ).first()

        #Get admin user.
        admin_user = User.query.filter(
            subquery.exists()
        ).first()

        assert normal_user.has_roles(['User']) is True
        assert admin_user.has_roles(['Admin']) is True
        assert admin_user.has_roles(['User']) is True
        assert admin_user.has_roles(['User', 'Admin']) is True
        assert normal_user.has_roles(['User', 'Admin']) is False
    

class TestBook:
    """Book model tests."""


    def test_get_or_404(self):
        """Test the get_or_404 method."""
        book = Book(title = 'title1', author='author1')
        db.session.add(book)
        db.session.commit()

        book_returned = Book.get_or_404(book.id)
        assert book == book_returned 
    

    def test_default_fields(self):
        """Test the default fields."""
        book = Book(title = 'title1', author='author1')
        db.session.add(book)
        db.session.commit()

        book_returned = Book.get_or_404(book.id)
        assert book_returned.isReserved == False
        assert book_returned.pages == 0
