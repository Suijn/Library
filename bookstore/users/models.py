from ..extensions import db, ma
from sqlalchemy.orm import relationship
from ..extensions import (bcrypt)


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    password = db.Column(db.LargeBinary(), nullable=False)
    email= db.Column(db.String(), nullable=False, unique=True)
    books = db.relationship("Book", back_populates='user')

    def __init__(self, password, email):
        self.set_password(password)
        self.email = email

    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password)

    
    def check_password(self, value):
        return bcrypt.check_password_hash(self.password, value)

    def __repr__(self):
        return f'{self.__class__}'

    
    def __str__(self):
        return f'id: {self.id}, username: {self.username}'


class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'password', 'email', 'books')