# JWT Flask Authentication

This package provide an easy way to handle authentication
in a flask application. By now it manages login and token required
constraint.

## How to use

You must have a user class defined like this:

```python
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash

db = SQLAlchemy()


class User(db.Model):
    ...
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(255))
    password = db.Column(db.String(255))
    ...

    def validate_password(self, password):
        return check_password_hash(self.password, password)

    ...
```

Then instanciate the Auth class and decorate view functions:

```python
from jwt_flask_auth import Auth
from flask import Flask
from models import User

app = Flask(__name__)
auth = Auth(
    user_class=User,
    user_id_field='id',
    username_field='username',
    password_field='password',
)


@app.route('/login', methods=['POST'])
def login():
    return auth.login()


@app.route('/protected')
@auth.token_required
def protected_route():
    return 'You have access'
```

Login will generate a token with a payload containing the user_id, username, and the expiration.

