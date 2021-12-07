from flask import json, request
from flask_testing import TestCase
from sqlalchemy import true

from server import app , Session, User,Wallet,Transaction
from server import bcrypt

class MyTest(TestCase):
    def create_app(self):
        return app

t_name="kop"
t_id="1"
tra_id="1"
t_value="10000"
tran_value="200"


class TestUser(MyTest):

    def setUp(self):
        self.user_username = t_name
        self.user_password = "somepassword"
        self.user_firstname = "kok"
        self.user_lastname = "fdb"
        self.user_auth = self.user_username, self.user_password
        self.user_firstname = "Example"
        self.user_data = {"username": self.user_username, "firstName": self.user_firstname,
                          "lastName": self.user_lastname, "password": self.user_password, }
        self.header = {"Content-Type": "application/json", }

    def test11_post_user(self):
        resp = self.client.post("http://localhost:5000/user", headers=self.header, data=json.dumps(self.user_data))
        self.assertEqual(200, resp.status_code)
        #self.assertGreaterEqual(resp.json().items(), dict(username=t_name).items())


    def test11_post_user_wrong(self):
        resp = self.client.post("http://localhost:5000/user", headers=self.header, data=json.dumps(self.user_data))
        self.assertEqual(409, resp.status_code)

    def test33_get_user(self):
        resp = self.client.get("http://localhost:5000/user/"+self.user_username, headers=self.header, auth=self.user_auth)
        self.assertEqual(resp.status_code, 200)

        self.assertEqual(resp.json, {**resp.json , **dict(username = self.user_username)})

    def test33_get_user_wrong(self):
        resp = self.client.get("http://localhost:5000/user/"+"user", headers=self.header, auth=self.user_auth)
        self.assertEqual(resp.status_code, 406)
        self.assertEqual(resp.data, b'{"error":"Access denied"}\n')

    def test55_put_user(self):
        resp = self.client.put("http://localhost:5000/user/"+self.user_username, headers=self.header,
                               auth=self.user_auth, data=json.dumps({"firstName": self.user_firstname , "lastName":"kok" , "email":"890","phone":"90"}))
        self.assertEqual(resp.status_code, 200)

    def test99_delete_user(self):
         resp = self.client.delete("http://localhost:5000/user/"+self.user_username, headers=self.header, auth=self.user_auth)
         self.assertEqual(resp.status_code, 200)


class TestWallet(MyTest):
    def setUp(self):
        self.user_username = "yu"
        self.user_password = "somepassword"
        self.wrong_auth="mal","12341322"
        self.user_auth = self.user_username, self.user_password
        self.header = {"Content-Type": "application/json", }
        self.wallet_id = t_id
        self.wallet_value=t_value
        self.wallet_owner_id="10"
        self.wallet_data = {"privacy" : 0 , "value": self.wallet_value,
                          "owner_id": self.wallet_owner_id  }

    def test11_post_wallet(self):
        resp = self.client.post("http://localhost:5000/wallet", headers=self.header, data=json.dumps(self.wallet_data),auth=self.user_auth)
        self.assertEqual(200, resp.status_code)


    def test33_get_wallet(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.get("http://localhost:5000/wallet/"+mi, headers=self.header,
                               auth=self.user_auth)
        self.assertEqual(resp.status_code, 200)

    def test33_get_wallet_wrong(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.get("http://localhost:5000/wallet/"+mi, headers=self.header,
                               auth=self.wrong_auth)
        self.assertEqual(resp.status_code, 406)

    def test55_put_wallet(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.put("http://localhost:5000/wallet/" + mi, headers=self.header,
                               auth=self.user_auth, data=json.dumps({"value": self.wallet_value ,"privacy" : 0 }))
        self.assertEqual(resp.status_code, 200)

    def test55_put_wallet_wrong(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.put("http://localhost:5000/wallet/" + mi, headers=self.header,
                               auth=self.wrong_auth, data=json.dumps({"value": self.wallet_value ,"privacy" : 0 }))
        self.assertEqual(resp.status_code, 406)

    def test55_get_wallet_rec(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.get("http://localhost:5000/wallet/" + mi+"/recipienters", headers=self.header,
                               auth=self.user_auth)
        self.assertEqual(resp.status_code, 200)

    def test55_get_wallet_sen(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.get("http://localhost:5000/wallet/" + mi+"/senders", headers=self.header,
                               auth=self.user_auth)
        self.assertEqual(resp.status_code, 200)


    def test99_delete_wallet(self):
        l = Session.query(Wallet).filter_by(value=t_value).first()
        mi = str(l.id)
        resp = self.client.delete("http://localhost:5000/wallet/" + mi, headers=self.header,
                                  auth=self.user_auth)
        self.assertEqual(resp.status_code, 200)



class TestTransaction(MyTest):
    def setUp(self):
        self.user_username = "yu"
        self.user_password = "somepassword"
        self.user_auth = self.user_username, self.user_password
        self.wrong_auth = "mal", self.user_password
        self.header = {"Content-Type": "application/json", }
        self.transaction_id=tra_id
        self.tra_sender="10"
        self.tr_recipient="21"
        self.tra_value=tran_value
        self.transaction_data = { "value": self.tra_value,
                          "sender_id": self.tra_sender, "recipient_id": self.tr_recipient, }

    def test11_post_transaction(self):
        resp = self.client.post("http://localhost:5000/transaction", headers=self.header, data=json.dumps(self.transaction_data))
        self.assertEqual(200, resp.status_code)

    def test11_post_transaction_wrong(self):
        resp = self.client.post("http://localhost:5000/transaction", headers=self.header, data=json.dumps({ "value": self.tra_value,
                          "sender_id": self.tra_sender, "recipient_id": "3457567", }))
        self.assertEqual(404, resp.status_code)

    def test11_post_transaction_wrong2(self):
        resp = self.client.post("http://localhost:5000/transaction", headers=self.header, data=json.dumps({ "value": self.tra_value,
                          "sender_id": "2572475", "recipient_id": self.tr_recipient, }))
        self.assertEqual(404, resp.status_code)

    def test33_get_transaction(self):
        l = Session.query(Transaction).filter_by(value=tran_value).first()
        mi = str(l.id)
        resp = self.client.get("http://localhost:5000/transaction/" + mi, headers=self.header)
        self.assertEqual(resp.status_code, 200)

    def test33_get_transaction_wrong(self):
        resp = self.client.get("http://localhost:5000/transaction/" + "1000", headers=self.header)
        self.assertEqual(resp.status_code, 404)

    def test55_put_transaction(self):
        l = Session.query(Transaction).filter_by(value=tran_value).first()
        mi = str(l.id)
        resp = self.client.put("http://localhost:5000/transaction/" + mi, headers=self.header,
                                data=json.dumps({"value": self.tra_value }))
        self.assertEqual(resp.status_code, 200)

    def test55_put_transaction_wrong1(self):
        l = Session.query(Transaction).filter_by(value=tran_value).first()
        mi = str(l.id)
        resp = self.client.put("http://localhost:5000/transaction/" + mi, headers=self.header,
                                data=json.dumps({"sender_id": 90 }))
        self.assertEqual(resp.status_code, 404)

    def test55_put_transaction_wrong2(self):
        l = Session.query(Transaction).filter_by(value=tran_value).first()
        mi = str(l.id)
        resp = self.client.put("http://localhost:5000/transaction/" + mi, headers=self.header,
                                data=json.dumps({"recipient_id": 90 }))
        self.assertEqual(resp.status_code, 404)

    def test99_delete_transaction(self):
        l = Session.query(Transaction).filter_by(value=tran_value).first()
        mi = str(l.id)
        resp = self.client.delete("http://localhost:5000/transaction/" + mi, headers=self.header,
                                  )
        self.assertEqual(resp.status_code, 200)

    def test99_delete_transaction_wrong(self):
        resp = self.client.delete("http://localhost:5000/transaction/" + "1000", headers=self.header)
        self.assertEqual(resp.status_code, 404)
