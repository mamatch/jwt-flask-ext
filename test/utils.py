import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from jwt_flask_ext import Auth
from .models import User, db

basedir = os.path.abspath(os.path.dirname(__file__))


def create_app():
    """A fnction to create an app"""

    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(os.path.join(basedir, 'user.db'))
    app.config['SECRET_KEY'] = 'Secret'
    db.init_app(app)

    auth = Auth(
        app=app,
        user_class=User,
        username_field='username',
        password_field='password',
        current_user_required=True,
        algorithm='HS256',
        expiration_seconds=30,
    )

    @app.route('/protected')
    @auth.token_required
    def index(current_user):
        return 'protected'

    @app.route('/login', methods=['POST'])
    def login():
        return auth.login()

    @app.route('/test')
    def test():
        return 'test ok'

    return app
