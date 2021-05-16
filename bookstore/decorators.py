from flask_jwt_extended import get_jwt_identity
from functools import wraps
from .users.models import User
from flask import abort, request
from .models import Book, Reservation
from sqlalchemy.exc import NoResultFound

def require_role(roles=["User"]):
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            current_user = User.query.get(get_jwt_identity())
            if current_user:
                if current_user.has_roles(roles):
                    return func(*args, **kwargs)
            return abort(401)
        return decorator
    return wrapper


def isAdminOrOwner():
    """A permission decorator that checks whether the user is an admin or the owner of the account he wants to modify"""
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            current_user = User.query.get(get_jwt_identity())
            if current_user:
                if current_user.id == int(kwargs['id']):
                    #User is the owner 
                    return func(*args, **kwargs)
                if current_user.has_role('Admin'):
                    #User is an Admin
                    return func(*args, **kwargs)
                return abort(401)
            return abort(401)
        return decorator
    return wrapper 


def isOwner():
    """A permission decorator to check whether the user is the owner of the account"""
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            current_user = User.query.get(get_jwt_identity())
            if current_user:
                if current_user.id == int(kwargs['id']):
                    return func(*args, **kwargs)
                return abort(401)
            return abort(401)
        return decorator
    return wrapper


def didReserveBook():
    """
    A permission decorator to check whether the user reserved the book.

    Scans the request for the book and user data. 
    """
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            data = request.get_json()
            if not data or 'book_id' not in data or 'user_id' not in data:
                abort(400)

            book = Book.get_or_404(data['book_id'])
            user = User.get_or_404(data['user_id'])

            try:
                reservation = Reservation.query.filter(
                    Reservation.reserved_by == user.id,
                    Reservation.book_id == book.id,
                    Reservation.status == 'STARTED'
                ).one()
            except NoResultFound:
                abort(401)
           
            if reservation:
                return func(*args, **kwargs)
            return abort(401)
        return decorator
    return wrapper
            

