import os
from flask import Flask, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from flask_mail import Mail, Message
from models import db, User, Address

BASEDIR = os.path.abspath(os.path.dirname(__file__))

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
db.init_app(app)

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

Migrate = Migrate(app, db)

Manager = Manager(app)
Manager.add_command('db', MigrateCommand)

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
       user = User(name=request.json.get('name'))
       db.session.add(user)
       db.session.commit()
       return jsonify(user.serialize()), 201


    if request.method == 'PUT':
        if id is not None:
            user = User.query.get(id)
            user.name = request.json.get('name')
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

@app.route('/sendmail', methods=['POST'])
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