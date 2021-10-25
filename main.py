from flask import Flask
from models import *

app = Flask(__name__)



if __name__ == "__main__":
    Base.metadata.create_all(engine)


