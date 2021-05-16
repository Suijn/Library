from flask_jwt_extended import get_jwt_identity
from functools import wraps
from .users.models import User
from flask import abort, request
from .models import Book, Reservation
from sqlalchemy.exc import NoResultFound
from marshmallow import ValidationError

def require_role(roles=["User"]):
    """
    A permission decorator to check whether the user is authorized to access a resource.

    :param roles: A list of roles. Defaults to 'User'.
    """
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
    A permission decorator to check whether the current user reserved the book.
    """
    def wrapper(func):
        @wraps(func)
        def decorator(*args, **kwargs):
            current_user = User.get_or_404(get_jwt_identity())

            try:
                reservation = Reservation.query.filter(
                    Reservation.reserved_by == current_user.id,
                    Reservation.book_id == kwargs['book_id'],
                    Reservation.status == 'STARTED'
                ).one()
            except NoResultFound:
                abort(401)
           
            if reservation:
                return func(*args, **kwargs)
            return abort(401)
        return decorator
    return wrapper
            

