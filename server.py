from flask import Flask, Response
from models import *
from flask import jsonify
import json
from flask import make_response
from flask import request
from sqlalchemy.exc import IntegrityError
from types import SimpleNamespace
from crypt import crypt

def crt(a):
    return crypt(a)[5:20]

def to_json(inst, cls):
    """
    Jsonify the sql alchemy query result.
    """
    convert = dict()
    d = dict()
    for c in cls.__table__.columns:
        v = getattr(inst, c.name)
        if c.type in convert.keys() and v is not None:
            try:
                d[c.name] = convert[c.type](v)
            except:
                d[c.name] = "Error:  Failed to covert using ", str(convert[c.type])
        elif v is None:
            d[c.name] = str()
        else:
            d[c.name] = v
    return json.dumps(d)


app = Flask(__name__)


# USER
@app.route("/user/<int:id>", methods=['GET'])
def get_user(id):
    print(get_user)
    try:
        a = to_json(Session.query(User).filter_by(id=id).one(), User)
        return Response(response=a,
                    status=200,
                    mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.route("/user/<string:username>", methods=['GET'])
def get_user_by_name(username):
    print(get_user_by_name)
    try:
        a = to_json(Session.query(User).filter_by(username=username).one(), User)
        return Response(response=a,
                    status=200,
                    mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/user', methods=['POST'])
def create_user():
    print("create_user")
    user = User(
        username = request.json.get('username'),
        firstName = request.json.get('firstName'),
        lastName = request.json.get('lastName'),
        email = request.json.get('email'),
        password = crt(request.json.get('password')),
        phone = request.json.get('phone'),
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

@app.route('/user/<int:id>', methods=['PUT'])
def update_user(id):
    print("update_user")
    u = Session.query(User).filter_by(id=id).first()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    if request.json.get('username'):
        tvins = (Session.query(User).filter_by(username=request.json.get('username')).all())
        if tvins != []:
            return make_response(jsonify({'error': 'username is busy'}), 409)
        u.username = request.json.get('username')
    if request.json.get('firstName'):
        u.firstName = request.json.get('firstName')
    if request.json.get('lastName'):
        u.lastName = request.json.get('lastName')
    if request.json.get('email'):
        u.email = request.json.get('email')
    if request.json.get('password'):
        u.password = crt(request.json.get('password'))
    if request.json.get('phone'):
        u.phone = request.json.get('phone')
    try:
        Session.commit()
        return Response(response=to_json(u, User),
                    status=200,
                    mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'uncorect data'}), 404)

@app.route('/user/<int:id>', methods=['DELETE'])
def delete_user(id):
    user = Session.query(User).filter_by(id=id).first()
    if not user:
        return make_response(jsonify({'error': 'Not found'}), 404)
    for i in user.wallets:
        for j in i.sended:
            Session.delete(j)
        for j in i.recipiented:
            Session.delete(j)
        Session.commit()
        Session.delete(i)
    Session.commit()
    Session.delete(user)
    Session.commit()
    return make_response(jsonify({'ok': 'user deleted'}), 20)


#WALLET
@app.route("/wallet/<int:id>", methods=['GET'])
def get_wallet(id):
    try:
        a = to_json(Session.query(Wallet).filter_by(id=id).one(), Wallet)
        return Response(response=a,
                    status=200,
                    mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'Not found'}), 404)

@app.route('/wallet', methods=['POST'])
def create_wallet():
    user = Wallet(
        value = request.json.get('value'),
        privacy = request.json.get('privacy'),
        owner_id = request.json.get('owner_id'),
    )
    
    if not Session.query(User).filter_by(id=request.json.get('owner_id')).first():
        return make_response(jsonify({'error': 'no user'}), 404)
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
def update_wallet(id):
    u = Session.query(Wallet).filter_by(id=id).first()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)        
    if request.json.get('value'):
        u.value = request.json.get('value')
    if request.json.get('privacy'):
        u.privacy = request.json.get('privacy')=="true"
    if request.json.get('owner_id'):
        if not Session.query(User).filter_by(id=request.json.get('owner_id')).first():
            print( "-----------except-------------")
            return make_response(jsonify({'error': 'no user'}), 404)
        u.owner_id = request.json.get('owner_id')
    try:
        Session.commit()
        return Response(response=to_json(u, Wallet),
                status=200,
                mimetype="application/json")
    except:
        return make_response(jsonify({'error': 'uncorect data'}), 404)

@app.route('/wallet/<int:id>', methods=['DELETE'])
def delete_walet(id):
    wallet = Session.query(Wallet).filter_by(id=id).first()
    if not wallet:
        return make_response(jsonify({'error': 'Not found'}), 404)
    for j in wallet.sended:
        Session.delete(j)
    for j in wallet.recipiented:
        Session.delete(j)
    Session.commit()
    Session.delete(wallet)
    Session.commit()
    return make_response(jsonify({'ok': 'wallet deleted'}), 20)




#TRANSACTION
@app.route('/transaction', methods=['POST'])
def create_transaction():
    t = Transaction(
        value = request.json.get('value'),
        sender_id = request.json.get('sender_id'),
        recipient_id = request.json.get('recipient_id'),
    )
    
    if not Session.query(Wallet).filter_by(id=t.sender_id).first():
        return make_response(jsonify({'error': 'no user'}), 404)
    if not Session.query(Wallet).filter_by(id=t.recipient_id).first():
        return make_response(jsonify({'error': 'no user'}), 404)
    try:
        Session.add(t)
        Session.commit()
    except:
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
    except:
        return make_response(jsonify({'error': 'uncorect data'}), 404)

@app.route('/transaction/<int:id>', methods=['DELETE'])
def delete_transaction(id):
    t = Session.query(Transaction).filter_by(id=id).first()
    if not t:
        return make_response(jsonify({'error': 'Not found'}), 404)
    Session.delete(t)
    Session.commit()
    return make_response(jsonify({'ok': 'transaction deleted'}), 20)



#ARRAYS
@app.route('/user/<int:id>/wallets', methods=['GET'])
def get_user_wallets(id):
    u = Session.query(User).filter_by(id=id).first()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    a = [to_json(i, Wallet) for i in u.wallets]
    return Response(response=str(a),
                    status=200,
                    mimetype="application/json")

@app.route('/wallet/<int:id>/senders', methods=['GET'])
def get_wallet_senders(id):
    u = Session.query(Wallet).filter_by(id=id).first()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    a = [to_json(i, Transaction) for i in u.sended]
    return Response(response=str(a),
                    status=200,
                    mimetype="application/json")

@app.route('/wallet/<int:id>/recipienters', methods=['GET'])
def get_wallet_recipienters(id):
    u = Session.query(Wallet).filter_by(id=id).first()
    if not u:
        return make_response(jsonify({'error': 'Not found'}), 404)
    a = [to_json(i, Transaction) for i in u.recipiented]
    return Response(response=str(a),
                    status=200,
                    mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)