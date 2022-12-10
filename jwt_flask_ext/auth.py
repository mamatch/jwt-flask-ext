from flask import Blueprint, request, jsonify, current_app, Flask
import jwt
import datetime
from functools import wraps


class Auth:
    """A class to encapsulate the handling of authentication(login and token required)

            Create an object to handle login and token_required decorator
            :param app: The flask app or the blueprint
            :param user_class:  The user class used for authentication
            :param password_validation_function: the function used to verify the validity of a password
            :param user_id_field: The user_id field's name in the user class
            :param username_field: The username field's name in the user class
            :param password_field: The password field's name in the user class
            :param current_user_required: Is the current_user is required (for session handle)
            :param algorithm: The algorithm useed to generate the token
            :param expiration_seconds: The duration of validity of a token in seconds
            """

    TOKEN_NOT_PROVIDED_MESSAGE = 'No token provided.'
    UNAUTHORIZED_MESSAGE = 'Unauthorized.'
    NO_LOGIN_PROVIDED_MESSAGE = 'No login provided.'
    SUCCESS_LOGIN_MESSAGE = 'Logged in.'
    LOGIN_ERROR_MESSAGE = 'Couldn\'t login.'

    def __init__(self, app: Flask | Blueprint, user_class,
                 user_id_field: str = 'id',
                 username_field: str = 'username',
                 password_field: str = 'password',
                 current_user_required: bool = False, algorithm: str = None,
                 expiration_seconds: int = 3600):

        self.app = app
        self.user_class = user_class
        self.user_id_field = user_id_field
        self.username_field = username_field
        self.password_field = password_field
        self.current_user_required = current_user_required
        self.algorithm = algorithm
        self.expiration_seconds = expiration_seconds

    def token_required(self, f):
        """Verify the presence of the token"""

        @wraps(f)
        def decorated(*args, **kwargs):
            # Get the token from Authorization header
            token = None
            if not request.headers['Authorization']:
                return jsonify({'message': self.TOKEN_NOT_PROVIDED_MESSAGE}), 401
            token = request.headers['Authorization'].split(' ')[1]

            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=[self.algorithm])
                current_user = self.user_class.query.filter_by(
                    **{self.username_field: data[self.username_field]}).first()
            except Exception as e:
                print(str(e))
                return jsonify({'message': self.UNAUTHORIZED_MESSAGE}), 403

            if self.current_user_required:
                return f(current_user, *args, **kwargs)
            else:
                return f(*args, **kwargs)

        return decorated

    def login(self):
        """Login a user and return a token if verified"""
        auth = request.form

        if not auth or not auth[self.username_field] or not auth[self.password_field]:
            return jsonify({'message': self.NO_LOGIN_PROVIDED_MESSAGE}), 401

        user = self.user_class.query.filter_by(**{self.username_field: auth[self.username_field]}).first()
        if user and user.validate_password(auth[self.password_field]):
            payload = {
                self.user_id_field: getattr(user, self.user_id_field),
                self.username_field: getattr(user, self.username_field),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expiration_seconds),
            }
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm=self.algorithm,
            )
            return jsonify({
                'message': self.SUCCESS_LOGIN_MESSAGE,
                'token': token,
            }), 200

        return jsonify({'message': self.LOGIN_ERROR_MESSAGE}), 401
