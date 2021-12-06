from flask import json
from flask_testing import TestCase

from server import app
from server import bcrypt


class MyTest(TestCase):
    def create_app(self):
        return app

class TestUser(MyTest):

    def setUp(self):
        self.user_id = "18"
        self.user_email = "someMail@gmail.com"
        self.user_password = "somepassword"
        self.user_auth = "someMail@gmail.com:somepassword"
        self.user_password_hashed = bcrypt.hashpw(self.user_password.encode("utf-8"), bcrypt.gensalt())

        self.user_data = {"email": "someMail@gmail.com", "password": "somepassword", }
        self.header = {"Content-Type": "application/json", }

    def test1_post_user(self):
        resp = self.client.post("http://localhost:5000/user", headers=self.header, data=json.dumps(self.user_data))

        self.assertEqual(200, resp.status_code)