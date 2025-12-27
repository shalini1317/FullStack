
from controller.database import db


class User(db.Model):
    __tablename__ = 'user'
    user_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    mobile_number = db.Column(db.Integer, nullable=False, unique=True)
    


    roles = db.relationship('Role', secondary='user_role', backref=db.backref('users', lazy='dynamic'))
    Listener = db.relationship('Listener', backref='user', lazy=True, uselist=False)
    Creator = db.relationship('Creator', backref='user', lazy=True, uselist=False)
    upload_song = db.relationship('Upload_Song', backref='creator', lazy=True)




class Role(db.Model):
    __tablename__ = 'role'
    role_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)


class UserRole(db.Model):
    __tablename__ = 'user_role'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))
    role_id = db.Column(db.Integer, db.ForeignKey('role.role_id'))


class Creator(db.Model):
    __tablename__ = 'creator'
    creator_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    flag = db.Column(db.Boolean, default=False)


class Listener(db.Model):
    __tablename__ = 'listener'
    listener_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    flag = db.Column(db.Boolean, default=False)



class Upload_Song(db.Model):
    __tablename__ = 'upload_song'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100))
    artist = db.Column(db.String(100))
    file_path= db.Column(db.String(200))
    creator_id = db.Column(db.Integer, db.ForeignKey('user.user_id'))

    playlist = db.relationship('Playlist_Upload_Song', back_populates='upload_song')



class Playlist(db.Model):
    __tablename__ = 'playlist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)

    upload_Song = db.relationship('Playlist_Upload_Song', back_populates='playlist')


class Playlist_Upload_Song(db.Model):
    __tablename__ = 'playlist_song'

    id = db.Column(db.Integer, primary_key=True)
    playlist_id = db.Column(db.Integer,db.ForeignKey('playlist.id'), nullable=False)
    upload_songs_id = db.Column( db.Integer, db.ForeignKey('upload_song.id'), nullable=False)

    playlist = db.relationship('Playlist', back_populates='upload_Song')
    upload_song = db.relationship('Upload_Song',back_populates='playlist')


class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    artist = db.Column(db.String(200))

  
