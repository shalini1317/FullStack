
from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
import os   
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from controller.config import Config
from controller.database import db
from controller.models import *
from controller.models import Upload_Song

#from controller.models import *

app = Flask(__name__)
app.config.from_object(Config)

# 🔹 CREATE UPLOAD FOLDER IF NOT EXISTS
# UPLOAD_FOLDER = 'static/songs'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

UPLOAD_FOLDER = os.path.join('static', 'songs')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_SONG'] = UPLOAD_FOLDER


app.config['UPLOAD_SONG'] = UPLOAD_FOLDER

db.init_app(app)  


with app.app_context():
    db.create_all()
    
    
    admin_role = Role.query.filter_by(name='admin').first()

    if not admin_role:
        admin_role = Role(name='admin')
        db.session.add(admin_role)


    creator_role = Role.query.filter_by(name='creator').first()
    if not creator_role:
        creator_role = Role(name='creator')
        db.session.add(creator_role)

    listener_role = Role.query.filter_by(name='listener').first()
    if not listener_role:
        listener_role = Role(name='listener')
        db.session.add(listener_role)

# ✅ Commit roles FIRST
    db.session.commit()


# ---------- CREATE ADMIN USER ----------
    admin_user = User.query.filter_by(name='ABC').first()

    if not admin_user:
        admin_user = User(
        name='ABC',
        email='admin@abc.com',
        password_hash=generate_password_hash('123456'),
        mobile_number = 15674839200,
        roles=[admin_role]
       )
    db.session.add(admin_user)
    db.session.commit()


@app.route('/')    
def home():
      return render_template('home.html')

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.user_id

            # get role safely
            # role_name = user.roles[0].name if user.roles else 'listener'
            # session['role'] = role_name
            roles = [role.name for role in user.roles]
            session['role'] = 'creator' if 'creator' in roles else 'listener'

            role_name = session['role']
            print("Logged in as:", role_name)
            if role_name == 'creator':
                return redirect(url_for('creator_dashboard'))
            else:
                return redirect(url_for('listener_dashboard'))

        # ❌ login failed
        flash("Invalid credentials")
        return render_template('login.html')

    # ✅ GET request
    return render_template('login.html')



# ---------------- REGISTER ----------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile_number = request.form['mobile_number']
        password = request.form['password']
        role_name = request.form['role']   # creator / listener


        if not role_name:
            return "Role not selected", 400


        # Email check
        if User.query.filter_by(email=email).first():
            flash("Email already exists")
            return redirect(url_for('register'))

        # Get role object
        role = Role.query.filter_by(name=role_name).first()

        # Create user
        user = User(
            name=name,
            email=email,
            password_hash=generate_password_hash(password, method="scrypt"),
            mobile_number=mobile_number,
            roles=[role]
        )
        db.session.add(user)
        db.session.flush()  # To get user_id before commit
        # 🔹 create creator / listener table entry
        if role_name == 'creator':
            creator = Creator(user_id=user.user_id)
            db.session.add(creator)
        else:
            listener = Listener(user_id=user.user_id)
            db.session.add(listener)


        db.session.commit()

        flash("Registration successful")
        return redirect(url_for('login'))

    return render_template('register.html')



@app.route('/creator/dashboard')
def creator_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template('creator_dashboard.html')



@app.route('/listener_dashboard')
def listener_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # All uploaded songs (creator songs)
    songs = Upload_Song.query.all()

    # Listener created playlists
    playlists = Playlist.query.filter_by(user_id=user_id).all()

    return render_template(
        'listener_dashboard.html',
        songs=songs,
        playlist=playlists
    )

    
@app.route('/my_songs')
def my_songs():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    songs = Upload_Song.query.filter_by(
        creator_id=session['user_id']
    ).all()

    return render_template('my_songs.html', songs=songs)
    

@app.route('/upload', methods=['GET', 'POST'])
def upload_song():
    # ✅ Only logged-in creators can upload
    if 'user_id' not in session or session.get('role') != 'creator':
        return redirect(url_for('login'))

    if request.method == 'POST':
        # 1️⃣ Get form data
        title = request.form['title']
        artist = request.form['artist']
        song_file = request.files['song']

        if song_file:
            # 2️⃣ Make filename safe
            filename = secure_filename(song_file.filename)

            # 3️⃣ Full path to save file
            file_path = os.path.join(app.config['UPLOAD_SONG'], filename)

            # 4️⃣ Save file physically
            song_file.save(file_path)

            # 5️⃣ Save song info in database
            new_song = Upload_Song(
                title=title,
                artist=artist,
                file_path=filename,
                creator_id=session['user_id']
            )

            db.session.add(new_song)
            db.session.commit()

            # 6️⃣ Redirect after upload
            return redirect(url_for('my_songs'))

        else:
            flash("No file selected", "error")
            return redirect(url_for('upload_song'))

    # GET request → show upload page
    return render_template('Upload_song.html')


# @app.route('/upload', methods=['GET', 'POST'])
# def upload_song():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         title = request.form['title']
#         artist = request.form['artist']
#         song_file = request.files['song']

#         filename = secure_filename(song_file.filename)
#         file_path = os.path.join(app.config['UPLOAD_SONG'], filename)

#         song_file.save(file_path)

#         new_song = Upload_Song(
#             title=title,
#             artist=artist,
#             file_path=file_path,
#             creator_id=session['user_id']
#         )

#         db.session.add(new_song)
#         db.session.commit()

#         return redirect(url_for('creator_dashboard'))

#     return render_template('Upload_song.html')

@app.route('/edit_song/<int:song_id>', methods=['GET', 'POST'])
def edit_song(song_id):
    if 'user_id' not in session or session.get('role') != 'creator':
        return redirect(url_for('login'))

    song = Upload_Song.query.get_or_404(song_id)

    # Ensure the logged-in creator owns this song
    if song.creator_id != session['user_id']:
        flash("Unauthorized access")
        return redirect(url_for('my_songs'))

    if request.method == 'POST':
        song.title = request.form['title']
        song.artist = request.form['artist']

        # Optional: update file
        song_file = request.files.get('song')
        if song_file and song_file.filename:
            filename = secure_filename(song_file.filename)
            song_file.save(os.path.join(app.config['UPLOAD_SONG'], filename))
            song.file_path = filename

        db.session.commit()
        flash("Song updated successfully")
        return redirect(url_for('my_songs'))

    return render_template('edit_song.html', song=song)


@app.route('/delete_song/<int:song_id>', methods=['POST'])
def delete_song(song_id):
    if 'user_id' not in session or session.get('role') != 'creator':
        return redirect(url_for('login'))

    song = Upload_Song.query.get_or_404(song_id)

    # Ensure the logged-in creator owns this song
    if song.creator_id != session['user_id']:
        flash("Unauthorized access")
        return redirect(url_for('my_songs'))

    # Optional: delete file physically
    file_path = os.path.join(app.config['UPLOAD_SONG'], song.file_path)
    if os.path.exists(file_path):
        os.remove(file_path)

    db.session.delete(song)
    db.session.commit()
    flash("Song deleted successfully")
    return redirect(url_for('my_songs'))




@app.route('/play')
def play():
    song_file = "mysong.mp3"   # coming from backend (DB later)
    return render_template('play_song.html', song=song_file)


# @app.route('/create_playlist', methods=['GET', 'POST'])
# def create_playlist():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))

#     if request.method == 'POST':
#         name = request.form['name']
#         playlist = Playlist(name=name, user_id=session['user_id'])
#         db.session.add(playlist)
#         db.session.commit()
#         return redirect(url_for('my_songs'))

#     return render_template('create_playlist.html')



    # playlist_song = Playlist_Upload_Song(
    #     playlist_id=playlist_id,
    #     upload_songs_id=song_id
    # )

    # db.session.add(playlist_song)
    # db.session.commit()

    # flash("Song added to playlist", "success")
    # return redirect(url_for('my_songs'))

@app.route('/play/<int:song_id>')
def play_song(song_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    song = Upload_Song.query.get_or_404(song_id)
    return render_template('play_song.html', song=song)


@app.route('/add_song/<int:song_id>', methods=['POST'])
def add_song_to_playlist(song_id):
    user_id = session.get('user_id')  # or current_user.id

    # 1️⃣ Get playlist
    playlist = Playlist.query.filter_by(user_id=user_id).first()

    # 2️⃣ If playlist not exists → create one
    if playlist is None:
        playlist = Playlist(
            name="My Playlist",
            user_id=user_id
        )
        db.session.add(playlist)
        db.session.commit()

    # 3️⃣ Add song to playlist
    playlist_song = Playlist_Upload_Song(
        playlist_id=playlist.id,
        upload_songs_id=song_id
    )
    db.session.add(playlist_song)
    db.session.commit()

    return redirect('/my_playlist')



@app.route('/my_playlist')
def my_playlist():
    user_id = session.get('user_id')

    # 1️⃣ Get user's playlist
    playlist = Playlist.query.filter_by(user_id=user_id).first()

    if playlist is None:
        playlist_songs = []
    else:
        # 2️⃣ GET SONGS FROM PLAYLIST  ✅ PASTE HERE
        playlist_songs = db.session.query(Upload_Song).join(
            Playlist_Upload_Song,
            Upload_Song.id == Playlist_Upload_Song.upload_songs_id
        ).filter(
            Playlist_Upload_Song.playlist_id == playlist.id
        ).all()

    # 3️⃣ Send to template
    return render_template(
        'my_playlist.html',
        playlist_songs=playlist_songs
    )


@app.route('/delete_song_from_playlist/<int:song_id>', methods=['POST'])
def delete_song_from_playlist(song_id):
    user_id = session.get('user_id')

    # Get user's playlist
    playlist = Playlist.query.filter_by(user_id=user_id).first()

    if playlist:
        playlist_song = Playlist_Upload_Song.query.filter_by(
            playlist_id=playlist.id,
            upload_song_id=song_id
        ).first()

        if playlist_song:
            db.session.delete(playlist_song)
            db.session.commit()

    # 🔴 IMPORTANT: RETURN RESPONSE
    return redirect(url_for('my_playlist'))


# @app.route('/my_playlist/<int:playlist_id>')
# def my_playlist(playlist_id):
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     playlist = Playlist.query.filter_by(user_id=session['user_id']).all()
#     return render_template('my_playlist.html', playlist=playlist)

    
@app.route('/dashboard')
def dashboard():
    role = session.get('role')

    if role == 'creator':
        return redirect(url_for('creator_dashboard'))
    elif role == 'listener':
        return redirect(url_for('listener_dashboard'))
    else:
        return redirect(url_for('login'))
    #===========
    # admin dashboard
    #===========


# Admin login route
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    from flask import request, flash
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        if email == email and password == password:
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            flash("Invalid email or password")
            return redirect(url_for('admin_login'))

    return render_template('admin_login.html')

# Admin logout
@app.route('/admin_logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# Admin dashboard route
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    # CREATOR VIEW: all songs uploaded by creators
    my_songs = Upload_Song.query.all()  # If you want creator-specific: filter by user_id

    # LISTENER VIEW: all songs for listener
    songs = Upload_Song.query.all()  # All songs available

    return render_template(
        'admin_dashboard.html',
        my_songs=my_songs,
        songs=songs
    )


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))    





if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)


