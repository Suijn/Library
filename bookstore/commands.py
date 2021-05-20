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

    #Create Admin and User roles if not found.
    try:
        admin_role = Role.query.filter_by(name='Admin').one()
    except NoResultFound as err:
        admin_role = Role('Admin')

    try:
        user_role = Role.query.filter_by(name='User').one()
    except NoResultFound as err:
        user_role = Role('User')    

    admin.roles.extend([admin_role, user_role])

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
        #If found, do nothing.
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
    A CLI command to assign a role to an existing user.
    
    Parameters:
        role_id,
        user_id
    """
    user = User.get_or_404(int(user_id))
    role = Role.query.get(int(role_id))

    if role not in user.roles:
        user.roles.append(role)
        db.session.commit()
