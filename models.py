from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from ext import db, login_manager

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    news_id = db.Column(db.Integer, db.ForeignKey('news.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    news = db.relationship('News', back_populates='comments')
    user = db.relationship('User', back_populates='comments')


class News(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String())
    descrip = db.Column(db.String())
    category = db.Column(db.String())
    img = db.Column(db.String())
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # რელაცია კომენტარებთან
    comments = db.relationship('Comment', back_populates='news', cascade="all, delete-orphan")


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key = True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    role =  db.Column(db.String())

    # რელაცია კომენტარებთან
    comments = db.relationship('Comment', back_populates='user')

    def __init__(self, username, password, role="Guest"):
        self.username = username
        self.password = generate_password_hash(password)
        self.role = role

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)