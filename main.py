from flask import Flask, render_template, request
from controller.config import Config
from controller.database import db
from controller.models import *


app = Flask(__name__)
app.config.from_object(Config)


db.init_app(app)

with app.app_context():
    db.create_all()
    

    # ---------- ROLES ----------
    admin_role = Role.query.filter_by(role_name='admin').first()
    if not admin_role:
        admin_role = Role(role_name='admin')
        db.session.add(admin_role)

    creator_role = Role.query.filter_by(role_name='creator').first()
    if not creator_role:
        creator_role = Role(role_name='creator')
        db.session.add(creator_role)

    listener_role = Role.query.filter_by(role_name='listener').first()
    if not listener_role:
        listener_role = Role(role_name='listener')
        db.session.add(listener_role)

    db.session.commit()  # ✅ commit roles first


    # ---------- ADMIN USER ----------
    admin_user = Users.query.filter_by(username='RRRADMIN').first()
    if not admin_user:
        admin_user = Users(
            username='RRRADMIN',
            email='admin@rrr.com',
            password_hash='admin123',
            Mobile_number='1234567890',
            flag=True
        )
        db.session.add(admin_user)
        db.session.commit()


    # ---------- ASSIGN ADMIN ROLE ----------
    admin_user_role = UserRoles.query.filter_by(
        user_id=admin_user.user_id,
        role_id=admin_role.role_id
    ).first()

    if not admin_user_role:
        admin_user_role = UserRoles(
            user_id=admin_user.user_id,
            role_id=admin_role.role_id
        )
        db.session.add(admin_user_role)

    db.session.commit()



    


@app.route("/")
def home():
    return render_template("home.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Handle registration logic here
        role = request.form.get('role')
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        mobile_number = request.form.get('mobile_number')
        confirm_password = request.form.get('confirm_password')


    if not (role and name and email and password and mobile_number and confirm_password):
        Flask('Please fill out all fields.', 'warning')
        return redirect(url_for('register'))
    if password != confirm_password:
        Flask('Passwords do not match.', 'warning')
        return redirect(url_for('register'))
    
    if Users.query.filter_by(email=email).first():
        Flask('Email already registered.', 'warning')
        return redirect(url_for('register'))


    hashed_password = generate_password_hash(password)
    new_user = Users(username=name, email=email, password_hash=hashed_password)
    db.session.add(new_user)  
    db.session.commit()


    #assign role
    role_obj = Role.query.filter_by(name=role).first()
    if not role_obj:
        role_obj = Role(name=role)
        db.session.add(role_obj)
        db.session.commit()
    new_user.roles.append(role_obj)   

    #create profile depending on role
    if role == 'listener':
        profile = Listener(user_id=new_user.user_id,
                           mobile_number=mobile_number,
                           flag=False)
        

    else:  # creator
        profile = Creator(user_id=new_user.user_id,
                           mobile_number=mobile_number,   
                            flag=False)
    db.session.add(profile)
    db.session.commit()


    Flask('Registration successful! Please login.', 'success')   
    return redirect(url_for('login'))
    return render_template('register.html')@app.route('/register', methods=['GET', 'POST'])

@app.route('/music')
def music():
    songs = [
        {"title": "Song One", "file": "song1.mp3"},
        {"title": "Song Two", "file": "song2.mp3"},
        {"title": "Song Three", "file": "song3.mp3"}
    ]
    return render_template('music.html', songs=songs)






if __name__ == "__main__":
    app.run()


