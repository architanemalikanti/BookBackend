
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Association table for bookmarked and posted books
user_books_association = db.Table(
    "user_books_association",
    db.Model.metadata,
    db.Column("user_id", db.Integer, db.ForeignKey("users.id")),
    db.Column("book_id", db.Integer, db.ForeignKey("books.id")),
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

    bookmarked_books = db.relationship(
        "Book", secondary=user_books_association, back_populates="bookmarked_by_users"
    )
    posted_books = db.relationship("Book", back_populates="posted_by_user", cascade="delete")

    def __init__(self, **kwargs):
        """
        Initialize User object/entry
        """
        self.username = kwargs.get("username")
        self.password = kwargs.get("password")
        self.profile_photo = kwargs.get("profile_photo")
        self.location = kwargs.get("location")

    def serialize(self):
        """
        Serialize a user object
        """
        return {
            "id": self.id,
            "username": self.username,
            "profile_photo": self.profile_photo,
            "location": self.location,
            "bookmarked_books": [book.simple_serialize() for book in self.bookmarked_books],
            "posted_books": [book.simple_serialize() for book in self.posted_books],
        }

    def simple_serialize(self):
        """
        Simple serialize a user object
        """
        return {
            "id": self.id,
            "username": self.username,
            "profile_photo": self.profile_photo,
        }


class Book(db.Model):
    """
    Book Model
    """
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=True)
    genre = db.Column(db.String, nullable=True)
    photos = db.Column(db.String, nullable=True)
    posted_by_user = db.relationship("User", back_populates="posted_books")
    bookmarked_by_users = db.relationship(
        "User", secondary=user_books_association, back_populates="bookmarked_books"
    )

    def __init__(self, **kwargs):
        """
        Initialize Book object/entry
        """
        self.name = kwargs.get("name")
        self.description = kwargs.get("description")
        self.genre = kwargs.get("genre")
        self.photos = kwargs.get("photos")
        self.user_id = kwargs.get("user_id")

    def serialize(self):
        """
        Serialize a book object
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "genre": self.genre,
            "photos": self.photos,
            "posted_by": self.posted_by_user.simple_serialize(),
        }

    def simple_serialize(self):
        """
        Simple serialize a book object
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "genre": self.genre,
            "photos": self.photos
        }