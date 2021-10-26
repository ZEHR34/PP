from flask import Flask
from models import *


app = Flask(__name__)

user1 = User(id=1, username="kuouo", firstName = "Yura",lastName = "Steb",email="a@gmail",password = "90",phone = "99999")
wallet1 = Wallet(id = 1 , privacy = False , owner_id = 1 , value = 9000)



with Session() as session:
    session.add(user1)
    session.add(wallet1)
    session.commit()

print(session.query(User).all()[0])




