import os
from flask import Flask, jsonify, request
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from models import db, User

BASEDIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'
app.config['DEBUG'] = True
app.config['ENV'] = 'development'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASEDIR, 'test.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

Migrate = Migrate(app, db)

Manager = Manager(app)
Manager.add_command('db', MigrateCommand)

@app.route('/users', methods=['GET', 'POST'])
@app.route('/users/<int:id>', methods=['GET', 'PUT', 'DELETE'])
def users(id=None):
    if request.method == 'GET':
        if id is not None:
            user = User.query.get(id)
            return jsonify(user.serialize()), 200
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



if __name__ == '__main__':
    Manager.run()