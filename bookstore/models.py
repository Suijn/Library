from .extensions import db, ma
from sqlalchemy.orm import relationship

class Book(db.Model):
    __tablename__ = 'books'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(), nullable=False)
    author = db.Column(db.String(), nullable=False)
    pages = db.Column(db.Integer, nullable=True)
    isReserved = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates='books')


    def __repr__(self):
        return f'{self.__class__}'
    
    
    def __str__(self):
        return f'id: {self.id}, title: {self.title}'

    
    def __init__(self, title, author):
        self.title = title
        self.author = author


class BookSchema(ma.Schema):
    class Meta:
        fields = ('id', 'title', 'author', 'pages', 'isReserved', 'user')
