from flask import Flask
from .users.models import User
from .extensions import (
    db,
    ma,
    bcrypt,
    jwt
)
import click
from . import commands
from . import users
from . import views


def create_app():
    app = Flask(__name__)

    app.config.from_object("bookstore.settings")
    
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)

    return app


def register_extensions(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
    ma.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)


def register_blueprints(app):
    app.register_blueprint(users.views.blueprint)
    app.register_blueprint(views.users.blueprint)
    app.register_blueprint(views.admins.blueprint)


def register_commands(app):
    app.cli.add_command(commands.create_admin_user)
    app.cli.add_command(commands.create_role)
    app.cli.add_command(commands.assign_role_to_user)





