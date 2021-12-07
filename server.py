from flask import Flask, Response

from flask import jsonify
import json
from flask import make_response
from flask import request
from sqlalchemy.exc import IntegrityError
from flask_httpauth import HTTPBasicAuth
from flask_bcrypt import Bcrypt

from flask_sqlalchemy import SQLAlchemy

from sqlalchemy import Integer, String, \
    Column, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.types import Boolean

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:stebelyura1337@localhost/pp_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
auth = HTTPBasicAuth()
bcrypt = Bcrypt(app)
Session = db.session


class User(db.Model):
    __tablename__ = "User"

    id = Column(Integer(), primary_key=True)
    username = Column(String(100), nullable=False)
    firstName = Column(String(100), nullable=False)
    lastName = Column(String(100), nullable=False)
    email = Column(String(100), nullable=True)
    password = Column(String(100), nullable=False)
    phone = Column(String(100), nullable=True)

    wallets = relationship("Wallet", backref="owner")


class Wallet(db.Model):
    __tablename__ = "Wallet"

    id = Column(Integer(), primary_key=True)
    privacy = Column(Boolean(), default=False)
    owner_id = Column(Integer(), ForeignKey(User.id), nullable=False)
    value = Column(Integer(), nullable=False)


class Transaction(db.Model):
    __tablename__ = "Transaction"

    id = Column(Integer(), primary_key=True)
    value = Column(Integer(), nullable=False)
    sender_id = Column(Integer(), ForeignKey(Wallet.id), nullable=False)
    recipient_id = Column(Integer(), ForeignKey(Wallet.id), nullable=False)

    sender = relationship("Wallet", foreign_keys="Transaction.sender_id", backref="sended")
    recipient = relationship("Wallet", foreign_keys="Transaction.recipient_id", backref="recipiented")


@auth.verify_password
def verify_password(username, password):
    user = db.session.query(User).filter_by(username=username).first()
    if not user:
        return False  # pragma: no cover
    if not bcrypt.check_password_hash(user.password.encode("utf-8"), password.encode("utf-8")):
        return False  # pragma: no cover

    if user:
        return user


def to_json(inst, cls):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:  # pragma: no cover
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)


# USER
@app.route("/user/<string:name>", methods=['GET'])
@auth.login_required
def get_user(name):
    print(get_user)
    user1 = auth.current_user()
    if user1.username != name:
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        a = to_json(Session.query(User).filter_by(username=name).one(), User)
        return Response(response=a,
                        status=200,
                        mimetype="application/json")
    except:  # pragma: no cover
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/user', methods=['POST'])
def create_user():
    print("create_user")
    user = User(
        username=request.json.get('username'),
        firstName=request.json.get('firstName'),
        lastName=request.json.get('lastName'),
        email=request.json.get('email'),
        password=bcrypt.generate_password_hash(str(request.json.get('password'))).decode('utf-8'),
        phone=request.json.get('phone'),
    )
    tvins = (Session.query(User).filter_by(username=user.username).all())
    if tvins != []:
        return make_response(jsonify({'error': 'username is busy'}), 409)
    try:
        Session.add(user)
        Session.commit()
    except IntegrityError:
        return make_response(jsonify({'error': 'uncorect data'}), 409)
    # tasks.append(task)
    a = to_json(user, User)
    return Response(response=a,
                    status=200,
                    mimetype="application/json")


@app.route('/user/<string:name>', methods=['PUT'])
@auth.login_required
def update_user(name):
    print("update_user")
    user1 = auth.current_user()
    if user1.username != name:
        return make_response(jsonify({'error': 'Access denied'}), 406)
    u = Session.query(User).filter_by(username=name).first()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if request.json.get('username'):
        u.username = request.json.get('username')
    if request.json.get('firstName'):
        u.firstName = request.json.get('firstName')
    if request.json.get('lastName'):
        u.lastName = request.json.get('lastName')
    if request.json.get('email'):
        u.email = request.json.get('email')
    if request.json.get('password'):
        u.password = bcrypt.generate_password_hash(str(request.json.get('password'))).decode('utf-8')
    if request.json.get('phone'):
        u.phone = request.json.get('phone')
    try:
        Session.commit()
        return Response(response=to_json(u, User),
                        status=200,
                        mimetype="application/json")
    except:  # pragma: no cover
        return make_response(jsonify({'error': 'uncorect data'}), 404)


@app.route('/user/<string:name>', methods=['DELETE'])
@auth.login_required
def delete_user(name):
    user1 = auth.current_user()
    if user1.username != name:
        return make_response(jsonify({'error': 'Access denied'}), 406)
    user = Session.query(User).filter_by(username=name).first()
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    Session.commit()
    Session.delete(user)
    Session.commit()
    return make_response(jsonify({'ok': 'user deleted'}), 200)


# WALLET
@app.route("/wallet/<int:id>", methods=['GET'])
@auth.login_required
def get_wallet(id):
    wallet = Session.query(Wallet).filter_by(id=id).one()
    user1 = auth.current_user()
    if user1.id != wallet.owner_id:
        return make_response(jsonify({'error': 'Access denied'}), 406)
    try:
        a = to_json(Session.query(Wallet).filter_by(id=id).one(), Wallet)
        return Response(response=a,
                        status=200,
                        mimetype="application/json")
    except:  # pragma: no cover
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/wallet', methods=['POST'])
@auth.login_required
def create_wallet():
    user1 = auth.current_user()
    user = Wallet(
        value=request.json.get('value'),
        privacy=request.json.get('privacy'),
        owner_id=user1.id,
    )

    try:
        Session.add(user)
        Session.commit()
    except:
        return make_response(jsonify({'error': 'uncorect data'}), 404)
    a = to_json(user, Wallet)
    return Response(response=a,
                    status=200,
                    mimetype="application/json")


@app.route('/wallet/<int:id>', methods=['PUT'])
@auth.login_required
def update_wallet(id):
    u = Session.query(Wallet).filter_by(id=id).first()
    user1 = auth.current_user()
    if user1.id != u.owner_id:
        return make_response(jsonify({'error': 'Access denied'}), 406)
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if request.json.get('value'):
        u.value = request.json.get('value')
    if request.json.get('privacy'):
        u.privacy = request.json.get('privacy') == "true"
    if request.json.get('owner_id'):
        u.owner_id = request.json.get('owner_id')
    try:
        Session.commit()
        return Response(response=to_json(u, Wallet),
                        status=200,
                        mimetype="application/json")
    except:  # pragma: no cover
        return make_response(jsonify({'error': 'uncorect data'}), 404)


@app.route('/wallet/<int:id>', methods=['DELETE'])
@auth.login_required
def delete_walet(id):
    wallet = Session.query(Wallet).filter_by(id=id).first()
    user1 = auth.current_user()
    if user1.id != wallet.owner_id:
        return make_response(jsonify({'error': 'Access denied'}), 406)
    if not wallet:
        return make_response(jsonify({'error': 'Not found'}), 404)
    Session.commit()
    Session.delete(wallet)
    Session.commit()
    return make_response(jsonify({'ok': 'wallet deleted'}), 200)


# TRANSACTION
@app.route('/transaction', methods=['POST'])
def create_transaction():
    m = 1000 - 7
    t = Transaction(
        value=request.json.get('value'),
        sender_id=request.json.get('sender_id'),
        recipient_id=request.json.get('recipient_id'),
    )

    if not Session.query(Wallet).filter_by(id=t.sender_id).first():
        return make_response(jsonify({'error': 'no user'}), 404)
    if not Session.query(Wallet).filter_by(id=t.recipient_id).first():
        return make_response(jsonify({'error': 'no user'}), 404)
    try:
        Session.add(t)
        Session.commit()
    except:  # pragma: no cover
        return make_response(jsonify({'error': 'uncorect data'}), 404)
    t.sender.value -= t.value
    t.recipient.value += t.value
    Session.commit()
    a = to_json(t, Transaction)
    return Response(response=a,
                    status=200,
                    mimetype="application/json")


@app.route("/transaction/<int:id>", methods=['GET'])
def get_transaction(id):
    try:
        a = to_json(Session.query(Transaction).filter_by(id=id).one(), Transaction)
        return Response(response=a,
                        status=200,
                        mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Not found'}), 404)


@app.route('/transaction/<int:id>', methods=['PUT'])
def update_transaction(id):
    u = Session.query(Transaction).filter_by(id=id).first()
    if not u:
        return make_response(jsonify({'error': 'not found'}), 404)
    if request.json.get('value'):
        u.value = request.json.get('value')
    if request.json.get('sender_id'):
        if not Session.query(Wallet).filter_by(id=request.json.get('sender_id')).first():
            return make_response(jsonify({'error': 'no sender'}), 404)
        u.sender_id = request.json.get('sender_id')
    if request.json.get('recipient_id'):
        if not Session.query(Wallet).filter_by(id=request.json.get('recipient_id')).first():
            return make_response(jsonify({'error': 'no recipient'}), 404)
        u.recipient_id = request.json.get('recipient_id')

    try:
        Session.commit()
        return Response(response=to_json(u, Transaction),
                        status=200,
                        mimetype="application/json")
    except:  # pragma: no cover
        return make_response(jsonify({'error': 'uncorect data'}), 404)


@app.route('/transaction/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    t = Session.query(Transaction).filter_by(id=id).first()

    if not t:
        return make_response(jsonify({'error': 'Not found'}), 404)
    Session.delete(t)
    Session.commit()
    return make_response(jsonify({'ok': 'transaction deleted'}), 200)


# ARRAYS


@app.route('/wallet/<int:id>/senders', methods=['GET'])
@auth.login_required
def get_wallet_senders(id):
    u = Session.query(Wallet).filter_by(id=id).first()
    user = auth.current_user()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)  # pragma: no cover
    if user.id != u.owner_id:
        return make_response(jsonify({'error': 'Access denied'}), 406)  # pragma: no cover
    a = [to_json(i, Transaction) for i in u.sended]
    return Response(response=str(a),
                    status=200,
                    mimetype="application/json")


@app.route('/wallet/<int:id>/recipienters', methods=['GET'])
@auth.login_required
def get_wallet_recipienters(id):
    u = Session.query(Wallet).filter_by(id=id).first()
    user = auth.current_user()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)  # pragma: no cover
    if user.id != u.owner_id:
        return make_response(jsonify({'error': 'Access denied'}), 406)  # pragma: no cover
    a = [to_json(i, Transaction) for i in u.recipiented]
    return Response(response=str(a),
                    status=200,
                    mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)  # pragma: no cover
