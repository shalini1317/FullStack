from controller.database import db

class Users(db.Model):
    __tablename__ = 'users'
    user_id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    Mobile_number = db.Column(db.String(15), nullable=False, unique=True)
    flag = db.Column(db.Boolean, default=False)


    roles = db.relationship('Role', secondary='user_roles', backref=db.backref('users', lazy='dynamic'))
    Listener_details = db.relationship('Listener', backref='user', lazy=True, uselist=False)
    Creator_details = db.relationship('Creator', backref='user', lazy=True, uselist=False)



class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    role_name = db.Column(db.String(50), nullable=False, unique=True)


class UserRoles(db.Model):
    __tablename__ = 'user_roles'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))   


class Creator(db.Model):
    __tablename__ = 'creator'
    creator_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    flag = db.Column(db.Boolean, default=False)


class Listener(db.Model):
    __tablename__ = 'listener'
    listener_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    flag = db.Column(db.Boolean, default=False)
