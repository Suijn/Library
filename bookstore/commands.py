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
        #If found do nothing.
        role = Role.query.filter_by(name=role_name).one() 
    except NoResultFound as err:
        role = Role(role_name)
        db.session.add(role)
        db.session.commit()


@click.command()
@with_appcontext
@click.argument('role_id', nargs=1)
@click.argument('user_id', nargs=1)
def assign_role_to_user(role_id, user_id):
    """
    A CLI command to add a role to an existing user.
    
    Parameters:
        role_id,
        user_id
    """
    user = User.get_or_404(user_id)
    role = Role.query.get(role_id)

    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
