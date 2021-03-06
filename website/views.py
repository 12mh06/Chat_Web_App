from time import process_time_ns
from flask import Blueprint, redirect, render_template, request, flash, jsonify, session, url_for
from flask_login import login_required, current_user
import json
from sqlalchemy import insert
from .models import Message, User, Chatroom
from . import db
from flask_socketio import SocketIO, emit, join_room, leave_room
from . import socket_io
import datetime

views = Blueprint('views', __name__)

# called when a message is sent in a chatroom; receives the message content and emits the message to all clients in the corresponsive room
@socket_io.on('send_message')
def send_message(msg_content):
    if session.get('chatroomId'):
        now = datetime.datetime.now()
        date = f"{now.year}-{now.month:02d}-{now.day:02d} {now.hour:02d}:{now.minute}:{now.second}"
        chatroomId = session['chatroomId']
        
        socket_io.emit('msg_data', {'msg_content' : msg_content, 'msg_date' : date, 'msg_sender' : current_user.first_name}, to= chatroomId)

# conncets users to the socket room when entering a chatroom
@socket_io.on('join')
def on_join():
    chatroomId = session['chatroomId']
    join_room(chatroomId)

    emit('conncetion_msg', f"{current_user.first_name} has been connceted to chatroom", to= chatroomId)
    
# disconnects user after closing a chatroom (the chatroom stays in user.chatrooms)
@socket_io.on('leave')
def on_leave():
    if session.get('chatroomId'):
        chatroomId = session['chatroomId']
        leave_room(chatroomId)
        emit('conncetcion_msg', f"{current_user.first_name} has been disconnected from chatroom", to= chatroomId)

# stores a new message in the database when a message is sent
@views.route('/add-message', methods= ['POST'])
@login_required
def add_message():
    if session.get('chatroomId'):
        print('YES')
        chatroomId = session["chatroomId"]
        data = json.loads(request.data)
        chatroom = Chatroom.query.get(chatroomId)
        msg_content = data['msgContent']
        if not msg_content:
            flash('message has to contain text', category= 'error')
        else:
            message = Message(content= msg_content)
            db.session.add(message)
            chatroom.messages.append(message)
            current_user.messages.append(message)
            db.session.commit()

    return jsonify({})

# adds user to a chatroom; the added user is not an active user (inside the chatroom in the moment), but can enter the chatroom 
@views.route('/add-to-chatroom', methods=['POST'])
@login_required
def add_to_chatroom():
    if session.get('chatroomId'):
        data = json.loads(request.data)
        friend_email = data['friendEmail']
        chatroomId = session["chatroomId"]
        
        chatroom = Chatroom.query.get(chatroomId)
        friend = User.query.filter_by(email= friend_email).first()
        if not friend:
            flash('user does not exist', category='error')
        elif friend not in current_user.friends:
            flash('user is not your friend', category='error')
        else:
            friend.chatrooms.append(chatroom)
            chatroom.users.append(friend)
            db.session.commit()
            flash('friend has been added to chatroom', category= 'success')

    return jsonify({})

# 'POST' method called when a chatroom name is typed and submitted. if the chatroom already exists the user is added to the chatroom
# otherwise the chatroom gets created and the user gets added simultaneously
@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if session.get('chatroomId'):
        chatroomId = session['chatroomId']
        chatroom = Chatroom.query.get(chatroomId)

        return render_template('home.html', user= current_user, chatroom= chatroom)  

    if request.method == 'POST':
        chatroom_name = request.form.get('chatroom-name')
        chatroom = Chatroom.query.filter_by(name= chatroom_name).first()

        if not chatroom_name:
            flash('name of chatroom needed', category='error')
        else:
            if not chatroom:
                chatroom = Chatroom(name= chatroom_name)
                db.session.add(chatroom)
                db.session.commit()
                flash('new chatroom created', category= 'sucess')

            chatroom.users.append(current_user)
            current_user.chatrooms.append(chatroom)
            db.session.commit()
            session['chatroomId'] = chatroom.id
            flash('joined chatroom', category= 'success')
    
    return render_template('home.html', user= current_user)  

# enters the user into the chosen chatroom. The user becomes an active user, a session with the chosen chatroom is created
@views.route('/enter-chatroom', methods= ['POST'])
@login_required
def enter_chatroom():
    chatroom = json.loads(request.data)
    chatroomId = chatroom['chatroomId']
    chatroom = Chatroom.query.get(chatroomId)
    session["chatroomId"] = chatroomId

    return jsonify({})

# deletes the session withe the chatroom Id, closing the chatroom for the user (user returns to list of chatrooms)
@views.route('/close-chatroom', methods= ['GET', 'POST'])
@login_required
def close_chatroom():
    if session.get('chatroomId'):
        chatroomId = session['chatroomId']
        chatroom = Chatroom.query.get(chatroomId)

        if chatroom:
            session.pop('chatroomId', None)
            flash('closed chatroom', category= 'success')
    
    return jsonify({})

# user is removed from chatroom-users and cannot enter the chatroom anymore 
@views.route('/leave-chatroom', methods= ['POST'])
@login_required
def leave_chatroom():
    chatroom = json.loads(request.data)
    chatroomId = chatroom['chatroomId']
    chatroom = Chatroom.query.get(chatroomId)
    if chatroom:
        current_user.chatrooms.remove(chatroom)
        db.session.commit()
        flash('you left the chatroom', category= 'sucess')

        if not chatroom.users:
            db.session.delete(chatroom)
            db.session.commit()
            flash('chatroom has been deleted because it had no users', category= 'success')

    return jsonify({})

# 'POST' method adds the current user to the chosen user's friendslist if the friend exists
# friend request from X to Y: => X in Y.friends; Y NOT in X.friends
@views.route('/friends', methods=['GET', 'POST'])
@login_required
def add_friends():
    if request.method == 'POST':
        email = request.form.get('email')
        new_friend = User.query.filter_by(email = email).first()

        if not new_friend:
            flash('there is no account linked to this email', category='error')
        elif new_friend.id == current_user.id:
            flash('you typed in your own email', category= 'error')
        elif new_friend in current_user.friends:
            flash('the user is alread your friend', category= 'error')
        else:
            new_friend.friends.append(current_user)
            db.session.commit()
            flash('friend request sent', category='success')

    return render_template("friends.html", user= current_user)

# friend request from X to Y: => X in Y.friends; Y NOT in X.friends
# if request is accepted: => X in Y.friends; Y in X.friends
# if request is denied: => X gets removed from Y.friends
@views.route('/respond-friend-request', methods= ['POST'])
@login_required
def accept_friend_request():
    data = json.loads(request.data)
    friendId = data['friendId']
    answer = data['answer']
    friend = User.query.get(friendId)
    if friend:
        if answer:
            friend.friends.append(current_user)
            db.session.commit()
            flash('friend request accepted', category='success')
        else:
            current_user.friends.remove(friend)
            flash('friend request denied', category='success')

    return jsonify({})

# friend gets removed from both friendlists
@views.route('/delete-friend', methods= ['POST'])
@login_required
def delete_friend():
    friend = json.loads(request.data)
    friendId = friend['friendId']
    friend = User.query.get(friendId)
    if friend:
        current_user.friends.remove(friend)
        friend.friends.remove(current_user)
        db.session.commit()
        flash('User has been unfriended', category= "success")

    return jsonify({})



