from datetime import datetime
from app import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_on = db.Column(db.DateTime(), default=datetime.utcnow)
    updated_on = db.Column(db.DateTime(), default=datetime.utcnow,  onupdate=datetime.utcnow)
    user_id = db.Column(db.String(100), unique=True)
    ip = db.Column(db.String(100), nullable=True)
    city = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    note = db.Column(db.String(100), nullable=True)
    
    def __repr__(self):
        return "<{}:{}>".format(self.id, self.username)
    
    
# class Victims(db.Model):
#     __tablename__ = 'victims'
#     id = db.Column(db.Integer, primary_key=True)
#     phone = db.Column(db.String(200), unique=True, nullable=False)
#     domain = db.Column(db.String(200), nullable=False)
#     date = db.Column(db.DateTime(), default=datetime.utcnow)
    
#     def __repr__(self):
#         return "<{}:{}>".format(self.id, self.username)