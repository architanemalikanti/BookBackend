import datetime
import hashlib
import os
import bcrypt
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for bookmarked and posted books
user_books_association = db.Table(
    "user_books_association",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("books.id"))
)

friendships = db.Table(
    "friendships",
    db.Model.metadata,
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('users.id'))
)

class User(db.Model):
    """
    User Model
    """
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    profile_photo = db.Column(db.String, nullable=True)
    location = db.Column(db.String, nullable=True)

    # User information
    email = db.Column(db.String, nullable=False, unique=True)
    password_digest = db.Column(db.String, nullable=False)

    # Session information
    session_token = db.Column(db.String, nullable=False, unique=True)
    session_expiration = db.Column(db.DateTime, nullable=False)
    update_token = db.Column(db.String, nullable=False, unique=True)

    bookmarked_books = db.relationship(
        "Book", secondary=user_books_association, back_populates="bookmarked_by_users"
    )
    posted_books = db.relationship("Book", back_populates="posted_by_user", cascade="delete")

    friends = db.relationship(
        "User", 
        secondary=friendships,  
        primaryjoin=(friendships.c.user_id == id),   # User's side of the relationship
        secondaryjoin=(friendships.c.friend_id == id),  # Friend's side of the relationshipsecondary=friendships,
        back_populates="friends"
    )

    def __init__(self, **kwargs):
        """
        Initialize User object/entry
        """
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.profile_photo = kwargs.get("profile_photo")
        self.location = kwargs.get("location")
        self.email = kwargs.get("email")
        self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf8"), bcrypt.gensalt(rounds=13))
        self.renew_session()

    def serialize(self):
        """
        Serialize a user object
        """
        return {
            "id": self.id,
            "username": self.username,
            "profile_photo": self.profile_photo,
            "location": self.location,
            "email": self.email,
            "bookmarked_books": [book.simple_serialize() for book in self.bookmarked_books],
            "posted_books": [book.simple_serialize() for book in self.posted_books],
            "friends": [friend.simple_serialize() for friend in self.friends]  # Serialize friends
        }

    def simple_serialize(self):
        """
        Simple serialize a user object
        """
        return {
            "id": self.id,
            "username": self.username,
            "profile_photo": self.profile_photo,
            "location": self.location,
            "email": self.email
        }

    def _urlsafe_base_64(self):
        """
        Randomly generates hashed tokens (used for session/update tokens)
        """
        return hashlib.sha1(os.urandom(64)).hexdigest()

    def renew_session(self):
        """
        Renews the sessions, i.e.
        1. Creates a new session token
        2. Sets the expiration time of the session to be a day from now
        3. Creates a new update token
        """
        self.session_token = self._urlsafe_base_64()
        self.session_expiration = datetime.datetime.now() + datetime.timedelta(minutes=1)
        self.update_token = self._urlsafe_base_64()

    def verify_password(self, password):
        """
        Verifies the password of a user
        """
        return bcrypt.checkpw(password.encode("utf8"), self.password_digest)

    def verify_session_token(self, session_token):
        """
        Verifies the session token of a user
        """
        return session_token == self.session_token and datetime.datetime.now() < self.session_expiration

    def verify_update_token(self, update_token):
        """
        Verifies the update token of a user
        """
        return update_token == self.update_token


class Book(db.Model):
    """
    Book Model
    """
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)

    image = db.Column(db.String, nullable=True)
    quote = db.Column(db.String, nullable=True)

    genre_id = db.Column(db.Integer, db.ForeignKey("genres.id"))  # Foreign key for genre
    genre = db.relationship("Genre", back_populates="books")

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)  # Foreign key for the user who posted
    posted_by_user = db.relationship("User", back_populates="posted_books")

    bookmarked_by_users = db.relationship(
        "User", secondary=user_books_association, back_populates="bookmarked_books"
    )

    def __init__(self, **kwargs):
        """
        Initialize Book object/entry
        """
        self.title = kwargs.get("title")
        self.author = kwargs.get("author")
        self.description = kwargs.get("description")
        self.image = kwargs.get("image")
        self.quote = kwargs.get("quote")
        self.genre = kwargs.get("genre")
        self.posted_by_user = kwargs.get("posted_by_user")

    def serialize(self):
        """
        Serialize a book object
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "image": self.image,
            "quote": self.quote,
            "genre": self.genre.simple_serialize(),
            "posted_by": self.posted_by_user.simple_serialize(),
        }

    def simple_serialize(self):
        """
        Simple serialize a book object
        """
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "description": self.description,
            "image": self.image,
            "quote": self.quote,
        }


class Genre(db.Model):
    __tablename__ = "genres"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    genre = db.Column(db.String, nullable=False, unique=True)
    books = db.relationship("Book", back_populates="genre", cascade="delete")

    def serialize(self):
        return {
            "id": self.id, 
            "genre": self.genre, 
            "books": [book.simple_serialize() for book in self.books]
        }
        
    def simple_serialize(self):
        return {
            "id": self.id, 
            "genre": self.genre, 
        }
    

