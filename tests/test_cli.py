"""A test module for testing cli commands."""

from bookstore import commands
from bookstore.users.models import User, Role, roles_users
from sqlalchemy.sql import exists, roles
from bookstore.extensions import db

from sqlalchemy.sql import text

def test_create_admin_user_OK(cli_runner):
    """
    Test the create_admin_user function.

    :assert: Admin user was created
    """
    args = ['admin@user.com', 'password']

    cli_runner.invoke(commands.create_admin_user, args)

    admin = User.query.filter(User.email == args[0]).one()

    assert admin
    assert admin.has_role('Admin')
    assert admin.has_role('User')


def test_create_admin_user_Email_Not_Unique(cli_runner, db_populate):
    """
    Test the create_admin_user function.

        If email is not unique:
    :assert: admin is not created, that is, there is only one user with provided email in the database.
    """
    args = ['admin@test.com', 'password']

    cli_runner.invoke(commands.create_admin_user, args)

    assert len(User.query.filter(User.email == args[0]).all()) == 1


def test_create_role_OK(cli_runner):
    """
    Test the create_role function.

    :assert: Admin and user roles were created.
    """

    args = ['Admin']
    cli_runner.invoke(commands.create_role, args)
    admin_role = Role.query.filter(Role.name == args[0]).one()

    args = ['User']
    cli_runner.invoke(commands.create_role, args)
    user_role = Role.query.filter(Role.name == args[0]).one()

    assert admin_role
    assert user_role


def test_create_role_Only_One_Role_In_Db(cli_runner, db_populate):
    """
    Test the create_role function.

        If roles are already present in the database.
    :assert: roles are not created, that is, there is only one role 'User' and only one role 'Admin' in the database.
    """
    args = ['Admin']
    cli_runner.invoke(commands.create_role, args)

    args = ['User']
    cli_runner.invoke(commands.create_role, args)

    assert len(Role.query.filter(Role.name == 'Admin').all()) == 1
    assert len(Role.query.filter(Role.name == 'User').all()) == 1


def test_assign_role_to_user_OK(cli_runner, db_populate):
    """
    Test the assign_role_to_user function.

    :assert: a role was assigned to the user.
    """
    admin_role = Role.query.filter(Role.name == 'Admin').one()

    # Get a normal user.
    subquery = db.session.query(roles_users).filter(
        roles_users.c.user_id == User.id,
        roles_users.c.role_id == admin_role.id
    )

    normal_user = User.query.filter(
        ~subquery.exists()
    ).first()

    user_id = normal_user.id
    args = [str(admin_role.id), str(user_id)]

    cli_runner.invoke(commands.assign_role_to_user, args)

    user = db.session.query(User).get_or_404(user_id)
    assert user.has_roles(['User','Admin'])




