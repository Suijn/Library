from flask_jwt_extended import get_jwt_identity
from functools import wraps
from .users.models import User
from flask import abort

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