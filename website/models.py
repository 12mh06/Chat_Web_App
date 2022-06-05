from sqlalchemy import ForeignKey
from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from flask_login import login_manager

# represents a recursive n to n relationship between Users
friends_table = db.Table(
    'friends_association', 
    db.Model.metadata, 
    db.Column('friends_id', db.Integer, primary_key= True),
    db.Column('user1_id', db.ForeignKey('user.id')),
    db.Column('user2_id', db.ForeignKey('user.id'))
    )

# represents a n to n relationship between Users and Chatroom 
chatroom_user_table = db.Table(
    'chatroom_association',
    db.Model.metadata, 
    db.Column('chatroom_relationship_id', db.Integer, primary_key= True),
    db.Column('user_id', db.ForeignKey('user.id')),
    db.Column('chatroom_id', db.ForeignKey('chatroom.id'))
)
    
# represents a user
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key= True)
    email = db.Column(db.String(100), unique= True, nullable= False)
    first_name = db.Column(db.String(100))
    password = db.Column(db.String(100), nullable= False)
    chatrooms = db.relationship('Chatroom', secondary= chatroom_user_table, back_populates= 'users')
    messages = db.relationship('Message', backref= 'user')
    friends = db.relationship(
        'User', secondary= friends_table, primaryjoin= id == friends_table.c.user2_id, secondaryjoin= id == friends_table.c.user1_id, backref= 'befrienders')
    
# stores the needed information to display a Message in a Chatroom
class Message(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    content = db.Column(db.String(300), nullable= True)
    date = db.Column(db.DateTime(timezone=True), default= func.now())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id', ondelete= 'CASCADE'))

# represents a Chatroom in which messages are sent 
class Chatroom(db.Model):
    id = db.Column(db.Integer, primary_key= True)
    name = db.Column(db.String(50), unique= True)
    messages = db.relationship('Message', cascade= 'all,delete',backref= 'chatroom')
    users = db.relationship('User', secondary= chatroom_user_table, back_populates= 'chatrooms')
    
    


    
