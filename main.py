from flask import Flask
from models import *


app = Flask(__name__)

user1 = User(id=1, username="kuouo", firstName = "Yura",lastName = "Steb",email="a@gmail",password = "90",phone = "99999")
user2 = User(id=2, username="kuouo", firstName = "Yura",lastName = "Steb",email="a@gmail",password = "90",phone = "99999")
wallet1 = Wallet(id = 1 , privacy = False , owner_id = 1 , value = 9000)
wallet2 = Wallet(id = 2 , privacy = False , owner_id = 2 , value = 9000)
trans = Transaction(id =1 , value = 903 , sender_id=wallet1.id ,recipient_id=wallet2.id)


with Session() as session:
    session.add(user1)
    session.add(user2)
    session.commit()
    session.add(wallet1)
    session.add(wallet2)
    session.commit()
    session.add(trans)
    session.commit()

print(session.query(User).all()[0])




