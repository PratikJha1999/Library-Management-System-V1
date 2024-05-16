from Library import db
from datetime import datetime,timedelta
from flask_login import UserMixin

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    bookrequest = db.relationship('BookRequest', back_populates='users', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'User("{self.id}", "{self.username}", "{self.email}")'


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable = False)
    password = db.Column(db.String(150), nullable = False)
    
    def __repr__(self) -> str:
        return f'User("{self.id}", "{self.username}")'
    

class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique = True)
    date_created = db.Column(db.DateTime, default = datetime.utcnow)
    desc = db.Column(db.String(1000))
    books = db.relationship('Books', back_populates='section', cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f'User("{self.id}", "{self.name}")'


class Books(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    content = db.Column(db.String(500))
    author = db.Column(db.String(1000))
    date_added = db.Column(db.DateTime, default = datetime.utcnow)
    section_name = db.Column(db.String(150), db.ForeignKey('section.name'))
    section = db.relationship('Section', back_populates='books')
    bookrequest = db.relationship('BookRequest', back_populates='books', cascade='all, delete-orphan')
    
    
    def __repr__(self) -> str:
        return f'User("{self.id}", "{self.name}")'

class BookRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer(), db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    date_requested = db.Column(db.DateTime, default = datetime.utcnow)
    date_issued = db.Column(db.DateTime)
    date_return = db.Column(db.DateTime)
    requested = db.Column(db.Boolean(), default = False)
    approved = db.Column(db.Boolean(), default = False)
    Ndays = db.Column(db.Integer)
    
    books = db.relationship('Books', back_populates='bookrequest',foreign_keys=[book_id])
    users = db.relationship('Users', back_populates='bookrequest',foreign_keys=[user_id])
    
    def approve(self):
        self.approved = True
        self.date_issued = datetime.now()
        self.date_return = self.date_issued + timedelta(days = self.Ndays)
    
    
    def __repr__(self) -> str:
        return f'User("{self.id}", "{self.book_name}")'
    
db.create_all()