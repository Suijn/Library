"""A test module for testing cli commands."""

from typing import get_args
from bookstore import commands
from bookstore.users.models import User, Role


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
