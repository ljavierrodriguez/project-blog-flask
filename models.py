from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()


class User(db.Model):
    __tablename__='users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    addresses = db.relationship('Address', backref='user', lazy=True)
    def __repr__(self):
        return '<User %r>' % self.name

    def serialize(self):
        json_list=None
        if self.addresses:
            json_list=[address.serialize() for address in self.addresses]

        return {
            "id": self.id,
            "name": self.name,
            "addresses": json_list
        }


class Address(db.Model):
    __tablename__='address'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'),
        nullable=False)

    def __repr__(self):
        return '<Address %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "user": self.user.name
        }