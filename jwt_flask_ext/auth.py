from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError, InvalidTokenError
from flask import Blueprint, request, jsonify, current_app, Flask
import jwt
import datetime
from functools import wraps


class NoLoginProvidedException(Exception):
    """ raised when no login has been provided """

class LoginErrorException(Exception):
    """ raised when there is error on loggin process """


class Auth:
    """A class to encapsulate the handling of authentication(login and token required)

    Create an object to handle login and token_required decorator
    :param app: The flask app or the blueprint
    :param user_class:  The user class used for authentication
    :param password_validation_function: the function used to verify the validity of a password
    :param username_field: The username field's name in the user class
    :param password_field: The password field's name in the user class
    :param current_user_required: Is the current_user is required (for session handle)
    :param algorithm: The algorithm useed to generate the token
    :param expiration_seconds: The duration of validity of a token in seconds
    """

    def __init__(self, app: Flask | Blueprint, user_class,
                 username_field: str = 'username',
                 password_field: str = 'password',
                 current_user_required: bool = False, algorithm: str = None,
                 expiration_seconds: int = 3600):

        self.app = app
        self.user_class = user_class
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
            if 'Authorization' not in request.headers:
                raise InvalidTokenError('No token provided.')

            token = request.headers['Authorization'].split(' ')[1]

            try:
                data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=[self.algorithm])
                current_user = self.user_class.query.filter_by(
                    **{self.username_field: data[self.username_field]}).first()
            except (DecodeError, InvalidSignatureError, ExpiredSignatureError) as exc:
                raise InvalidTokenError from exc

            if self.current_user_required:
                return f(current_user, *args, **kwargs)
            else:
                return f(*args, **kwargs)

        return decorated

    def login(self):
        """Login a user and return a token if verified"""
        auth = request.form

        if not auth or not auth[self.username_field] or not auth[self.password_field]:
            raise NoLoginProvidedException('No login provided.')

        user = self.user_class.query.filter_by(**{self.username_field: auth[self.username_field]}).first()
        if user and user.validate_password(auth[self.password_field]):
            payload = {
                self.username_field: getattr(user, self.username_field),
                'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=self.expiration_seconds),
            }
            token = jwt.encode(
                payload,
                current_app.config['SECRET_KEY'],
                algorithm=self.algorithm,
            )
            return jsonify({
                'token': token,
            }), 200

        raise LoginErrorException( 'Couldn\'t login.')
