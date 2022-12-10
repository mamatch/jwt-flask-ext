from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(100), nullable=False)

    @property
    def password(self, password: str):
        raise AttributeError('password is not a valid attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        """Validate password"""
        return check_password_hash(self.password_hash, password)

    def from_dict(self, data):
        try:
            for attr in ['username', 'password']:
                setattr(self, attr, data[attr])
        except KeyError as e:
            print(str(e))

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
        }

    @staticmethod
    def create(data):
        """Create a user from dict"""
        user = User()
        user.from_dict(data)
        return user
