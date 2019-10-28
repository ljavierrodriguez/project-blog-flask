import os
from flask import Flask, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from flask_cors import CORS

from flask_jwt import JWT, jwt_required, current_identity
from werkzeug.security import safe_str_cmp

from models import db, User, Address

import datetime

BASEDIR = os.path.abspath(os.path.dirname(__file__))

def authenticate(username, password):
    user = User.query.filter_by(username=username).first()
    if user and safe_str_cmp(user.password.encode('utf-8'), password.encode('utf-8')):
        return user

def identity(payload):
    user_id = payload['identity']
    return User.query.get(user_id)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'ljavierrodriguez@gmail.com'
app.config['MAIL_PASSWORD'] = ''
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['JWT_EXPIRATION_DELTA'] = datetime.timedelta(days=3)
db.init_app(app)
CORS(app)

'''
MAIL_SERVER : default ‘localhost’
MAIL_PORT : default 25
MAIL_USE_TLS : default False
MAIL_USE_SSL : default False
MAIL_DEBUG : default app.debug
MAIL_USERNAME : default None
MAIL_PASSWORD : default None
MAIL_DEFAULT_SENDER : default None
MAIL_MAX_EMAILS : default None
MAIL_SUPPRESS_SEND : default app.testing
MAIL_ASCII_ATTACHMENTS : default False
'''

mail = Mail()
mail.init_app(app)

jwt = JWT(app, authenticate, identity)

Migrate = Migrate(app, db)

Manager = Manager(app)
Manager.add_command('db', MigrateCommand)


@app.route('/register', methods=['POST'])
def register():
    if request.method=='POST':
        user = User(
           name=request.json.get('name'), 
           username=request.json.get('username'),
           password=request.json.get('password')
        )
        db.session.add(user)
        db.session.commit()
        return jsonify({"message":"registro exitoso"}), 201

@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def users(id=None):
    if request.method == 'GET':
        if id is not None:
            user = User.query.get(id)
            if user:
                return jsonify(user.serialize()), 200
            else:
                return jsonify({"error":"not found"}), 404
        else:
            users = User.query.all()
            json_list=[user.serialize() for user in users]
            return jsonify(json_list), 200

    if request.method == 'POST':
       user = User(
           name=request.json.get('name'), 
           username=request.json.get('username'),
           password=request.json.get('password'))
       db.session.add(user)
       db.session.commit()
       return jsonify(user.serialize()), 201


    if request.method == 'PUT':
        if id is not None:
            user = User.query.get(id)
            user.name = request.json.get('name')
            if request.json.get('password'):
                user.password = request.json.get('password')
            db.session.commit()
            return jsonify(user.serialize()), 201
    
    if request.method == 'DELETE':
        if id is not None:
            user = User.query.get(id)
            db.session.delete(user)
            db.session.commit()
            return jsonify({"message":"object deleted"}), 200


@app.route('/addresses', methods=['GET', 'POST'])
@app.route('/addresses/<int:id>', methods=['GET', 'PUT', 'DELETE'])
@jwt_required()
def addresses(id=None):
    if request.method == 'GET':
        if id is not None:
            address = Address.query.get(id)
            if address:
                return jsonify(address.serialize()), 200
            else:
                return jsonify({"error":"not found"}), 404
        else:
            addresses = Address.query.all()
            json_list=[address.serialize() for address in addresses]
            return jsonify(json_list), 200

    if request.method == 'POST':
       address = Address(email=request.json.get('email'), user_id=request.json.get('user_id'))
       db.session.add(address)
       db.session.commit()
       return jsonify(address.serialize()), 201


    if request.method == 'PUT':
        if id is not None:
            address = Address.query.get(id)
            address.email = request.json.get('email')
            address.user_id = request.json.get('user_id')
            db.session.commit()
            return jsonify(address.serialize()), 201
    
    if request.method == 'DELETE':
        if id is not None:
            address = Address.query.get(id)
            db.session.delete(address)
            db.session.commit()
            return jsonify({"message":"object deleted"}), 200

@app.route('/sendmail', methods=['GET'])
def sendmail():
    msg = Message('Hello', 
        sender = 'ljavierrodriguez@gmail.com', 
        recipients = ['lrodriguez@4geeks.co']
    )
    msg.subject = "Esto es una prueba"
    msg.html = "<h1>Hola Mundo</h1>"
    mail.send(msg)

    return jsonify({"message":"Email sent"}), 200


if __name__ == '__main__':
    Manager.run()