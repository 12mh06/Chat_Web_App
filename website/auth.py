from flask import Blueprint, render_template, request, flash, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.sql import text
import sqlalchemy as sql
from .models import Chatroom, User
from flask_login import login_user, login_required, logout_user, current_user
from . import db

auth = Blueprint('auth', __name__)

#logs user in with email and password
@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        
        if not user:
            flash('email has no account', category= 'error')
        elif not check_password_hash(user.password, password):
            flash('wrong password!', category= 'error')
        else:
            login_user(user, remember= True)
            flash('User was Logged in', category= 'success')
            return redirect(url_for('views.home'))


    return render_template("login.html", user= current_user)

#logs user out
@auth.route('/logout')
@login_required
def logout():
    chatroom = Chatroom.query.get(current_user.active_chatroom_id)
    if chatroom:
        chatroom.active_users.remove(current_user)
        
    logout_user()
    return redirect(url_for('auth.login'))

# sings user in with email, name, password
# checks if email and password are valid (formatting, lentgth, etc.)
@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        if len(email) < 4:
            flash("Email too short", category="error")
        elif email.count('@') != 1:
            flash("Email must contain a '@'", category="error")
        elif User.query.filter_by(email= email):
            flash("Email already has an account", category="error")
        elif len(first_name) < 1:
            flash("First Name too short", category="error")
        elif password1 != password2:
            flash("passwords not equal", category="error")
        elif len(password1) < 4:
          flash("password too short", category="error")
        else:
            new_user = User(email= email, first_name= first_name, password= generate_password_hash(password1, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            flash('Acccount created', category='success')

            return redirect(url_for('auth.login')) 

    return render_template("sign-up.html", user= current_user)
