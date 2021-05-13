import click
from flask.cli import with_appcontext
from .extensions import db
from .users.models import User, Role
from sqlalchemy.exc import NoResultFound

@click.command()
@with_appcontext
@click.argument('email', nargs=1)
@click.argument('password', nargs=1)
def create_admin_user(email, password):
    """
    A CLI command to create a super user.
    
    Parameters
    ----------
        email,
        password
    """
    admin = User(password, email)

    #Create an Admin role if it's not in database yet.
    try:
        role = Role.query.filter_by(name='Admin').one()
    except NoResultFound as err:
        role = Role('Admin')
    
    admin.roles.append(role)

    db.session.add(admin)
    db.session.commit()

@click.command()
@with_appcontext
@click.argument('role_name', nargs=1)
def create_role(role_name):
    """
    A CLI command to create a role.
    
    Parameters:
        role_name
    """

    try:
        role = Role.query.filter_by(name=role_name).one()
    except NoResultFound as err:
        role = Role(role_name)
    
    db.session.add(role)
    db.session.commit()
