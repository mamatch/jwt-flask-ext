import os
import unittest
from flask import Flask, current_app
from .models import User, db
import requests
from .utils import create_app
from jwt_flask_ext.auth import NoLoginProvidedException, LoginErrorException
from jwt.exceptions import DecodeError, ExpiredSignatureError, InvalidSignatureError, InvalidTokenError



class TestAuth(unittest.TestCase):
    def setUp(self) -> None:
        self.app = create_app()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.drop_all()
        db.create_all()
        self.user1 = User.create({
            'username': 'John',
            'password': 'JohnWick',
        })
        db.session.add(self.user1)
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self) -> None:
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_user_add(self):
        user = User.create({
            'username': 'Jack',
            'password': 'Jack007',
        })
        db.session.add(user)
        db.session.commit()
        users = User.query.all()
        self.assertEqual(len(users), 2)

    def test_login_without_data(self):
        self.assertRaises(NoLoginProvidedException, self.client.post, '/login')

    def test_login_without_wrong_data(self):
        self.assertRaises(
            LoginErrorException,
            self.client.post,
            '/login',
            data={
                'username': 'Oo',
                'password': 'sdfd',
            }
        )

    def test_login_without_good_data(self):
        response = self.client.post(
            '/login',
            data={
                'username': 'John',
                'password': 'JohnWick',
            }
        )
        self.assertTrue('token' in response.json)

    def test_token_required_denied(self):
        token = self.client.post(
            '/login',
            data={
                'username': 'John',
                'password': 'JohnWick',
            }
        )
        token = token.json['token']
        headers = {
            'Authorization': f'Bearer {token}'
        }
        access = self.client.get('/protected', headers=headers)
        self.assertEqual(access.text, 'protected')

    def test_token_required_no_header(self):
        self.assertRaises(InvalidTokenError, self.client.get, '/protected')

    def test_token_required_bad_header(self):
        self.assertRaises(InvalidTokenError, self.client.get, '/protected', headers={'Authorization': 'Bearer fgsdfsdfsd'})

    def test_app_exists(self):
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):
        self.assertTrue(current_app.config['TESTING'])
